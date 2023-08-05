from os import path
from subprocess import run
from typing import Optional

from copernicus_marine_client.catalogue_parser.catalogue_parser import (
    CopernicusMarineCatalogue,
    get_product_from_url,
    parse_catalogue,
)
from copernicus_marine_client.catalogue_parser.request_structure import (
    SubsetRequest,
)


def parse_motu_dataset_url(data_path: str) -> str:
    host = data_path.split("/motu-web/Motu")[0] + "/motu-web/Motu"
    return host


def download_motu(
    login: str,
    password: str,
    subset_request: SubsetRequest,
    catalogue: Optional[CopernicusMarineCatalogue],
):
    if not catalogue:
        catalogue = parse_catalogue()
    dataset_url = subset_request.dataset_url
    if not dataset_url:
        raise TypeError(
            "Variable 'dataset_url' should not be empty in function 'download_motu()'"
        )
    product = get_product_from_url(catalogue, dataset_url)
    product_id = product.product_id
    if not subset_request.dataset_id:
        dataset_id = product.datasets[0].dataset_id
    else:
        dataset_id = subset_request.dataset_id
    if not subset_request.output_filename:
        output_filename = "data.nc"
    else:
        output_filename = subset_request.output_filename
    if not subset_request.output_directory:
        output_directory = "."
    else:
        output_directory = subset_request.output_directory
    options_list = [
        "--motu",
        parse_motu_dataset_url(str(subset_request.dataset_url)),
        "--service-id",
        product_id + "-TDS",
        "--product-id",
        dataset_id,
        "--out-dir",
        output_directory,
        "--out-name",
        output_filename,
        "--user",
        login,
        "--pwd",
        password,
    ]

    if subset_request.minimal_longitude is not None:
        options_list.extend(
            [
                "--longitude-min",
                str(subset_request.minimal_longitude),
            ]
        )
    if subset_request.maximal_longitude is not None:
        options_list.extend(
            [
                "--longitude-max",
                str(subset_request.maximal_longitude),
            ]
        )
    if subset_request.minimal_latitude is not None:
        options_list.extend(
            [
                "--latitude-min",
                str(subset_request.minimal_latitude),
            ]
        )
    if subset_request.maximal_latitude is not None:
        options_list.extend(
            [
                "--latitude-max",
                str(subset_request.maximal_latitude),
            ]
        )
    if subset_request.minimal_depth is not None:
        options_list.extend(
            [
                "--depth-min",
                str(subset_request.minimal_depth),
            ]
        )
    if subset_request.maximal_depth is not None:
        options_list.extend(
            [
                "--depth-max",
                str(subset_request.maximal_depth),
            ]
        )
    if subset_request.start_datetime:
        options_list.extend(
            [
                "--date-min",
                str(subset_request.start_datetime),
            ]
        )
    if subset_request.end_datetime:
        options_list.extend(
            [
                "--date-max",
                str(subset_request.end_datetime),
            ]
        )

    if subset_request.variables:
        options_list.extend(
            [
                flat
                for var in subset_request.variables
                for flat in ["--variable", var]
            ]
        )
    run(
        [
            "motuclient",
        ]
        + options_list
    )
    return path.join(output_directory, output_filename)
