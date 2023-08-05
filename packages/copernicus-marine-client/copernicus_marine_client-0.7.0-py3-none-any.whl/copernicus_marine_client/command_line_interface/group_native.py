import click

from copernicus_marine_client.catalogue_parser.catalogue_parser import (
    FTP_KEY,
    S3NATIVE_KEY,
    get_protocol_from_url,
    get_protocol_url_from_id,
)
from copernicus_marine_client.catalogue_parser.request_structure import (
    NativeRequest,
    native_request_from_file,
)
from copernicus_marine_client.download_functions.download_ftp import (
    download_ftp,
)
from copernicus_marine_client.download_functions.download_s3native import (
    download_s3native,
)

PROTOCOL_KEYS_ORDER = {"s3native": S3NATIVE_KEY, "ftp": FTP_KEY}


@click.group()
def cli_group_native() -> None:
    pass


@cli_group_native.command(
    "native",
    help="""Downloads native data files based on
    dataset_id or datafiles url path.
    The function fetches the files recursively if a folder path is passed as url.
    When provided a dataset id,
    all the files in the corresponding folder will be downloaded.

    By default for any download request, a summary of the request result is
    displayed to the user and a confirmation is asked.
    This can be turned down.
Example:

  copernicus-marine native -nd -o data_folder --dataset-id
  cmems_mod_nws_bgc-pft_myint_7km-3D-diato_P1M-m

  copernicus-marine native -nd -o data_folder --dataset-url
  ftp://my.cmems-du.eu/Core/NWSHELF_MULTIYEAR_BGC_004_011/cmems_mod_nws_bgc-pft_myint_7km-3D-diato_P1M-m
""",
)
@click.option(
    "--dataset-url",
    "-u",
    type=str,
    help="Path to the data files",
)
@click.option(
    "--dataset-id",
    "-i",
    type=str,
    help="The dataset id",
)
@click.option(
    "--login",
    prompt=True,
    hide_input=False,
)
@click.option(
    "--password",
    prompt=True,
    hide_input=True,
)
@click.option(
    "--no-directories",
    "-nd",
    is_flag=True,
    help="Option to not recreate folder hierarchy" + " in ouput directory.",
    default=False,
)
@click.option(
    "--show-outputnames",
    is_flag=True,
    help="Option to display the names of the"
    + " output files before download.",
    default=False,
)
@click.option(
    "--output-directory",
    "-o",
    type=click.Path(),
    help="The destination directory for the downloaded files."
    + " Default is the current directory",
)
@click.option(
    "--assume-yes",
    is_flag=True,
    default=False,
    help="Whether to ask for confirmation before download, after header display. "
    "If 'True', skips confirmation.",
)
@click.option(
    "--force-protocol",
    type=click.Choice(list(PROTOCOL_KEYS_ORDER.keys())),
    help="Force download through one of the available protocols",
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Flag to specify NOT to send the request to external server. "
    "Returns the request instead",
)
@click.option(
    "--request-file",
    type=click.Path(),
    help="Option to pass a file containg CLI arguments. "
    "The file MUST follow the structure of dataclass 'NativeRequest'. ",
)
def native(
    dataset_url: str,
    dataset_id: str,
    login: str,
    password: str,
    no_directories: bool,
    show_outputnames: bool,
    output_directory: str,
    assume_yes: bool,
    request_file: str,
    force_protocol: str,
    dry_run: bool,
):
    native_request = NativeRequest()
    if request_file:
        native_request = native_request_from_file(request_file)
    request_update_dict = {
        "dataset_url": dataset_url,
        "dataset_id": dataset_id,
        "output_directory": output_directory,
        "force_protocol": force_protocol,
    }
    native_request.update(request_update_dict)
    # Specific treatment for default values:
    # In order to not overload arguments with default values
    if no_directories:
        native_request.no_directories = no_directories
    if show_outputnames:
        native_request.show_outputnames = show_outputnames
    if assume_yes:
        native_request.assume_yes = assume_yes
    if force_protocol:
        native_request.force_protocol = force_protocol
    if dry_run:
        native_request.dry_run = dry_run

    native_function(
        login,
        password,
        native_request,
    )


def native_function(
    login: str,
    password: str,
    native_request: NativeRequest,
):
    if native_request.force_protocol:
        click.echo(
            f"You forced selection of protocol: {native_request.force_protocol}"
        )
    possible_protocols = (
        list(PROTOCOL_KEYS_ORDER.values())
        if not native_request.force_protocol
        else [PROTOCOL_KEYS_ORDER[native_request.force_protocol]]
    )
    if not native_request.dataset_url:
        if not native_request.dataset_id:
            raise SyntaxError(
                "Must specify at least one of 'dataset_url' or 'dataset_id'"
            )
        protocol, native_request.dataset_url = get_protocol_url_from_id(
            native_request.dataset_id, possible_protocols
        )
    else:
        protocol = get_protocol_from_url(native_request.dataset_url)
        if (
            protocol != native_request.force_protocol
            and native_request.force_protocol is not None
        ):
            raise ValueError(
                f"Forced protocol {native_request.force_protocol} does not match "
                f"user-specified url {native_request.dataset_url}"
            )
    if protocol == FTP_KEY:
        if native_request.dry_run:
            print(
                "download_ftp("
                + ", ".join(
                    [
                        f"{login}",
                        "HIDING_PASSWORD",
                        f"{native_request}",
                    ]
                )
                + ")"
            )
            return

        download_summary = download_ftp(
            login,
            password,
            native_request,
        )
        click.echo(download_summary)
    elif protocol == S3NATIVE_KEY:
        if native_request.dry_run:
            print(
                "download_s3native("
                + ", ".join(
                    [
                        f"{login}",
                        "HIDING_PASSWORD",
                        f"{native_request}",
                    ]
                )
                + ")"
            )
            return

        download_summary = download_s3native(
            login,
            password,
            native_request,
        )
        click.echo(download_summary)
    else:
        raise TypeError(f"Protocol type not handled: {protocol}")
