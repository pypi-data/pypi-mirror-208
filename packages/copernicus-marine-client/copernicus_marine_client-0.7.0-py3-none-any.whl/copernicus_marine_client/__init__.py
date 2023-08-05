"""
.
"""

from copernicus_marine_client.catalogue_parser.catalogue_parser import (
    CopernicusMarineCatalogue as CopernicusMarineCatalogue,
)
from copernicus_marine_client.catalogue_parser.catalogue_parser import (
    CopernicusMarineDatasetCoordinates as CopernicusMarineDatasetCoordinates,
)
from copernicus_marine_client.catalogue_parser.catalogue_parser import (
    CopernicusMarineDatasetService as CopernicusMarineDatasetService,
)
from copernicus_marine_client.catalogue_parser.catalogue_parser import (
    CopernicusMarineDatasetVariable as CopernicusMarineDatasetVariable,
)
from copernicus_marine_client.catalogue_parser.catalogue_parser import (
    CopernicusMarineProduct as CopernicusMarineProduct,
)
from copernicus_marine_client.catalogue_parser.catalogue_parser import (
    CopernicusMarineProductDataset as CopernicusMarineProductDataset,
)
from copernicus_marine_client.catalogue_parser.catalogue_parser import (
    CopernicusMarineProductProvider as CopernicusMarineProductProvide,
)
from copernicus_marine_client.catalogue_parser.catalogue_parser import (
    parse_catalogue as fetch_catalogue,
    get_all_dataset_ids as get_all_dataset_ids,
    merge_catalogues as merge_catalogues,
    parse_dissemination_unit_catalogue as fetch_dissemination_unit_catalogue,
    parse_marine_data_store_catalogue as fetch_marine_data_store_catalogue,
)


from copernicus_marine_client.catalogue_parser.request_structure import (
    NativeRequest as NativeRequest,
    native_request_from_file as native_request_from_file
    )
from copernicus_marine_client.catalogue_parser.request_structure import (
    SubsetRequest as SubsetRequest,
    subset_request_from_file as subset_request_from_file, 
    convert_motu_api_request_to_structure as convert_motu_api_request_to_structure
    )
from copernicus_marine_client.command_line_interface.group_native import (
    PROTOCOL_KEYS_ORDER as NATIVE_PROTOCOL_KEYS_ORDER,
)
from copernicus_marine_client.command_line_interface.group_native import (
    native_function as download_native,
)
from copernicus_marine_client.command_line_interface.group_subset import (
    PROTOCOL_KEYS_ORDER as SUBSET_PROTOCOL_KEYS_ORDER,
)
from copernicus_marine_client.command_line_interface.group_subset import open_dataset as open_dataset
from copernicus_marine_client.command_line_interface.group_subset import (
    subset_function as download_subset,
)
from copernicus_marine_client.download_functions.download_ftp import download_ftp as download_ftp
from copernicus_marine_client.download_functions.download_motu import download_motu as download_motu
from copernicus_marine_client.download_functions.download_opendap import (
    download_opendap as download_opendap,
)
from copernicus_marine_client.download_functions.download_s3native import (
    download_s3native as download_s3native,
)
from copernicus_marine_client.download_functions.download_zarr import download_zarr as download_zarr
from copernicus_marine_client.download_functions.download_zarr import (
    get_optimized_chunking as get_optimized_chunking,
)
