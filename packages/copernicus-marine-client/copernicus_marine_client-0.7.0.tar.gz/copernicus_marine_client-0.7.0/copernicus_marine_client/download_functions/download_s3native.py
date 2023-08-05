import subprocess
from multiprocessing.pool import ThreadPool
from subprocess import CompletedProcess
from typing import Tuple

import click
from numpy import append, arange
from tqdm import tqdm

from copernicus_marine_client.catalogue_parser.request_structure import (
    NativeRequest,
)


def download_s3native(
    login: str,
    password: str,
    native_request: NativeRequest,
) -> str:
    message, endpoint_url, filenames_in = download_header(
        [str(native_request.dataset_url)], login, password
    )
    filenames_out = create_filenames_out(
        filenames_in,
        native_request.output_directory,
        native_request.no_directories,
    )
    click.echo(message)
    if native_request.show_outputnames:
        click.echo("Output filenames:")
        [click.echo(filename_out) for filename_out in filenames_out]
    if not native_request.assume_yes:
        click.confirm("Do you want to continue?", abort=True)
    pool = ThreadPool()
    nfiles_per_process, nfiles = 1, len(filenames_in)
    indexes = append(
        arange(0, nfiles, nfiles_per_process, dtype=int),
        nfiles,
    )
    groups_in_files = [
        filenames_in[indexes[i] : indexes[i + 1]]
        for i in range(len(indexes) - 1)
    ]
    groups_out_files = [
        filenames_out[indexes[i] : indexes[i + 1]]
        for i in range(len(indexes) - 1)
    ]
    download_summary_list = pool.map(
        download_files,
        zip(
            [endpoint_url] * len(groups_in_files),
            groups_in_files,
            groups_out_files,
        ),
    )
    download_summary = "".join(map(str, download_summary_list))
    return download_summary


def download_header(
    data_paths: list[str], login: str, password: str
) -> Tuple[str, str, list[str]]:

    path_dict = parse_s3native_dataset_url(data_paths)
    message = "You requested the download of the following files:\n"
    filenames, sizes, total_size = [], [], 0.0
    for endpoint_url, paths in path_dict.items():
        for path in paths:
            files_name_size = get_filenames_recursively(endpoint_url, path)
            for filename, size in files_name_size:
                filenames += [filename]
                sizes += [float(size)]
                total_size += float(size)
    for filename, size in files_name_size[:20]:
        message += str(filename)
        message += f" - {format_file_size(float(size))}\n"
        if len(filenames) > 20:
            message += f"Printed 20 out of {len(filenames)} files\n"
    message += (
        f"\nTotal size of the download: {format_file_size(total_size)}\n\n"
    )
    return (message, endpoint_url, filenames)


def get_filenames_recursively(
    endpoint_url: str,
    path: str,
    files_already_found: list[tuple[str, str]] = [],
) -> list[tuple[str, str]]:
    if not path.endswith("/"):
        path += "/"
    bash_command: str = (
        f"s5cmd --endpoint-url {endpoint_url} --no-sign-request ls {path}"
    )
    raw_output: CompletedProcess[bytes] = subprocess.run(
        bash_command, shell=True, capture_output=True
    )
    cleaned_output: str = raw_output.stdout.decode("utf-8").strip()
    lines: list[str] = [
        substr.strip() for substr in cleaned_output.split("\n")
    ]
    for line in lines:
        if not line:
            pass
        elif line.startswith("DIR"):
            files_already_found.extend(
                get_filenames_recursively(
                    endpoint_url, path + line.split(" ")[-1].strip(), []
                )
            )
        elif line.endswith(".nc"):
            files_already_found.extend(
                [
                    (
                        path + line.split(" ")[-1].split("/")[-1],
                        line.split(" ")[-2],
                    )
                ]
            )
        else:
            raise ValueError(f"Unable to handle line: {line}")
    return files_already_found


def download_files(
    tuple_s3native_filename: Tuple[str, list[str], list[str]],
) -> str:
    def _s3native_file_download(
        endpoint_url: str, file_in: str, file_out: str
    ) -> str:
        """
        Download ONE file and return a string of the result
        """
        bash_command = (
            f"s5cmd --endpoint-url {endpoint_url} --no-sign-request "
            f"cp --no-clobber {file_in} {file_out}"
        )
        with tqdm(desc=file_in.split("/")[-1]) as t:
            """
            Comment: for now s5cmd does not seem to have a way to display progress
            (see https://github.com/peak/s5cmd/issues/51)
            """
            raw_output: CompletedProcess[bytes] = subprocess.run(
                bash_command, shell=True, capture_output=True
            )
            t.update()
        if not raw_output.stdout.decode("utf-8"):
            summary_string = f"File {file_out} already exists\n"
        else:
            summary_string = f"File {file_out} created\n"
        return summary_string

    endpoint_url, filenames_in, filenames_out = tuple_s3native_filename
    download_summary = ""
    for file_in, file_out in zip(filenames_in, filenames_out):
        download_summary += _s3native_file_download(
            endpoint_url, file_in, file_out
        )
    return download_summary


# /////////////////////////////
# --- Tools
# /////////////////////////////


def parse_s3native_dataset_url(data_paths: list[str]) -> dict:
    path_dict: dict[str, list[str]] = {}
    for data_path in data_paths:
        endpoint_url, path = data_path.split("/mdl-native/", maxsplit=1)
        path = "s3://mdl-native/" + path
        path_dict.setdefault(endpoint_url, []).append(path)
    return path_dict


def create_filenames_out(
    filenames_in: list[str], output_directory: str = "", no_directories=False
) -> list[str]:
    filenames_out = []
    for filename_in in filenames_in:
        filename_out = f"{output_directory}/"
        if no_directories:
            filenames_out += [filename_out + filename_in.split("/")[-1]]
        elif filename_in.startswith("s3://mdl-native/native/"):
            filenames_out += [
                filename_out + filename_in[len("s3://mdl-native/native/") :]
            ]
    return filenames_out


def format_file_size(
    size: float, decimals: int = 2, binary_system: bool = False
) -> str:
    if binary_system:
        units: list[str] = [
            "B",
            "KiB",
            "MiB",
            "GiB",
            "TiB",
            "PiB",
            "EiB",
            "ZiB",
        ]
        largest_unit: str = "YiB"
        step: int = 1024
    else:
        units = ["B", "kB", "MB", "GB", "TB", "PB", "EB", "ZB"]
        largest_unit = "YB"
        step = 1000

    for unit in units:
        if size < step:
            return ("%." + str(decimals) + "f %s") % (size, unit)
        size /= step

    return ("%." + str(decimals) + "f %s") % (size, largest_unit)
