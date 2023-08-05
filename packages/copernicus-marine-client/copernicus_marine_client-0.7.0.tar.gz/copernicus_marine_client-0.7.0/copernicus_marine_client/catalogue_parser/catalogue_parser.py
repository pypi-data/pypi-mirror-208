from copy import deepcopy
from dataclasses import dataclass
from datetime import timedelta
from itertools import groupby
from json import loads
from multiprocessing import Pool
from typing import Any, Callable, Iterable, Optional, Tuple, TypeVar, Union

import requests
from cachier import cachier
from pystac import Asset, Catalog, Collection, Item, Link, STACError
from tqdm import tqdm


@dataclass
class CopernicusMarineDatasetService:
    protocol: str
    uri: str


@dataclass
class CopernicusMarineDatasetCoordinates:
    coordinates_id: str
    units: str
    minimum_value: float
    maximum_value: float
    step: Optional[float]
    values: Optional[str]


@dataclass
class CopernicusMarineDatasetVariable:
    short_name: str
    standard_name: str
    units: str
    bbox: Tuple[float, float, float, float]
    coordinates: list[CopernicusMarineDatasetCoordinates]


@dataclass
class CopernicusMarineProductDataset:
    dataset_id: str
    dataset_name: str
    services: list[CopernicusMarineDatasetService]
    variables: list[CopernicusMarineDatasetVariable]


@dataclass
class CopernicusMarineProductProvider:
    name: str
    roles: list[str]
    url: str
    email: str


@dataclass
class CopernicusMarineProduct:
    title: str
    product_id: str
    thumbnail_url: str
    description: str
    production_center: str
    creation_datetime: str
    modified_datetime: Optional[str]
    keywords: dict[str, str]
    datasets: list[CopernicusMarineProductDataset]


@dataclass
class CopernicusMarineCatalogue:
    products: list[CopernicusMarineProduct]

    def filter(self, tokens: list[str]):
        return filter_catalogue_with_strings(self, tokens)


OPENDAP_KEY = "opendap"
MOTU_KEY = "motu"
FTP_KEY = "ftp"
GEOCHUNKED_KEY = "geoChunked"
TIMECHUNKED_KEY = "timeChunked"
S3NATIVE_KEY = "native"
DOWNSAMPLED4_KEY = "downsampled4"

_S = TypeVar("_S")
_T = TypeVar("_T")


def map_parallel(
    function: Callable[[_S], _T], iterable: Iterable[_S]
) -> list[_T]:
    parallel_processes = 20
    with Pool(parallel_processes) as pool:
        return pool.map(function, iterable)


def map_reject_none(
    function: Callable[[_S], Optional[_T]], iterable: Iterable[_S]
) -> Iterable[_T]:
    return (element for element in map(function, iterable) if element)


def parse_catalogue(
    overwrite_cache: bool = False,
) -> CopernicusMarineCatalogue:
    return merge_catalogues(
        parse_dissemination_unit_catalogue(overwrite_cache=overwrite_cache),
        parse_marine_data_store_catalogue(overwrite_cache=overwrite_cache),
    )


# --------------------------------------------------------
# --- Function specific for cmems-be.lobelia catalogue ---
# --------------------------------------------------------
@cachier(stale_after=timedelta(hours=3))
def _fetch_raw_products() -> list[dict[str, Any]]:
    response = requests.post(
        "https://cmems-be.lobelia.earth/api/datasets",
        json={"size": 1000, "includeOmis": True},
    )
    assert response.ok, response.text
    raw_catalogue: dict[str, Any] = loads(response.text)
    return map_parallel(
        _fetch_raw_product,
        tqdm(
            raw_catalogue["datasets"].keys(),
            desc="Fetching dissemination unit raw products",
        ),
    )


def _fetch_raw_product(product_id: str) -> dict[str, Any]:
    response = requests.get(product_url(product_id))
    assert response.ok, response.text
    return loads(response.text)


def product_url(product_id: str) -> str:
    return (
        f"https://cmems-be.lobelia.earth/api/dataset/{product_id}"
        + "?variant=detailed-v2"
    )


def variable_title_to_standard_name(variable_title: str) -> str:
    return variable_title.lower().replace(" ", "_")


def variable_to_pick(layer: dict[str, Any]) -> bool:
    return (
        layer["variableId"] != "__DEFAULT__"
        and layer["subsetVariableIds"]
        and len(layer["subsetVariableIds"]) == 1
    )


def to_datasets(
    raw_services: dict[str, dict[str, str]], layers: dict[str, dict[str, Any]]
) -> list[CopernicusMarineProductDataset]:
    def to_service(
        protocol_uri: Tuple[str, str]
    ) -> CopernicusMarineDatasetService:
        return CopernicusMarineDatasetService(
            protocol=protocol_uri[0], uri=protocol_uri[1]
        )

    def to_variable(layer: dict[str, Any]) -> CopernicusMarineDatasetVariable:
        def to_coordinates(
            subset_attributes: Tuple[str, dict[str, Any]]
        ) -> CopernicusMarineDatasetCoordinates:
            coordinate_name = subset_attributes[0]
            values: Optional[str]
            if coordinate_name == "depth":
                values = layer.get("zValues")
            elif coordinate_name == "time":
                values = layer.get("tValues")
            else:
                values = None
            return CopernicusMarineDatasetCoordinates(
                coordinates_id=subset_attributes[0],
                units=subset_attributes[1]["units"],
                minimum_value=subset_attributes[1]["min"],
                maximum_value=subset_attributes[1]["max"],
                step=subset_attributes[1].get("step"),
                values=values,
            )

        return CopernicusMarineDatasetVariable(
            short_name=layer["variableId"],
            standard_name=variable_title_to_standard_name(
                layer["variableTitle"]
            ),
            units=layer["units"],
            bbox=layer["bbox"],
            coordinates=list(
                map(to_coordinates, layer["subsetAttrs"].items())
            ),
        )

    def to_dataset(
        dataset_group: Tuple[str, Iterable[dict[str, Any]]],
    ) -> CopernicusMarineProductDataset:
        dataset_id = dataset_group[0]
        layer_elements = list(dataset_group[1])
        return CopernicusMarineProductDataset(
            dataset_id=dataset_id,
            dataset_name=layer_elements[0]["subdatasetTitle"],
            services=list(map(to_service, raw_services[dataset_id].items())),
            variables=list(
                map(to_variable, filter(variable_to_pick, layer_elements))
            ),
        )

    groups = groupby(layers.values(), key=lambda layer: layer["subdatasetId"])
    return sorted(
        map(to_dataset, groups), key=lambda dataset: dataset.dataset_id
    )


def _parse_product(raw_product: dict[str, Any]) -> CopernicusMarineProduct:
    return CopernicusMarineProduct(
        title=raw_product["title"],
        product_id=raw_product["id"],
        thumbnail_url=raw_product["thumbnailUrl"],
        description=raw_product["abstract"],
        production_center=raw_product["originatingCenter"],
        creation_datetime=raw_product["creationDate"],
        modified_datetime=raw_product.get("modifiedDate"),
        keywords=raw_product["keywords"],
        datasets=to_datasets(raw_product["services"], raw_product["layers"]),
    )


def parse_dissemination_unit_catalogue(
    overwrite_cache: bool = False,
) -> CopernicusMarineCatalogue:
    raw_products: list[dict[str, Any]] = _fetch_raw_products(
        overwrite_cache=overwrite_cache
    )

    return CopernicusMarineCatalogue(
        products=sorted(
            map(_parse_product, raw_products),
            key=lambda product: product.product_id,
        ),
    )


# ------------------------------------------------
# --- Function specific for MDS STAC catalogue ---
# ------------------------------------------------

MDS_STAC_BASE_URL = (
    "https://s3.waw3-1.cloudferro.com/mdl-metadata/metadata/catalog.stac.json"
)


@cachier(stale_after=timedelta(hours=3))
def _fetch_stac_raw_data() -> list[Tuple[Collection, list[Item]]]:
    stac_catalogue = Catalog.from_file(MDS_STAC_BASE_URL)
    products = [
        stac_product
        for stac_product in map_parallel(
            _create_collection,
            tqdm(
                stac_catalogue.get_child_links(),
                desc="Fetching marine data store raw products",
            ),
        )
        if stac_product
    ]
    return map_parallel(
        _fetch_stac_datasets,
        tqdm(products, desc="Fetching marine data store raw datasets"),
    )


def _fetch_stac_datasets(
    stac_product: Collection,
) -> Tuple[Collection, list[Item]]:
    return (
        stac_product,
        [
            stac_dataset
            for stac_dataset in map(
                _create_item, stac_product.get_item_links()
            )
            if stac_dataset
        ],
    )


def _create_collection(link: Link) -> Union[Collection, None]:
    try:
        return Collection.from_file(link.get_absolute_href())
    except KeyError as e:
        messages = ["spatial", "temporal"]
        if e.args[0] not in messages:
            raise KeyError(e.args)
        return None


def _create_item(link: Link) -> Union[Item, None]:
    try:
        return Item.from_file(link.get_absolute_href())
    except STACError as e:
        message = (
            "Invalid Item: If datetime is None, a start_datetime "
            + "and end_datetime must be supplied."
        )
        if e.args[0] != message:
            raise STACError(e.args)
        return None


def parse_marine_data_store_catalogue(
    overwrite_cache: bool = False,
) -> CopernicusMarineCatalogue:
    stac_raw_data = _fetch_stac_raw_data(overwrite_cache=overwrite_cache)
    products = map_reject_none(_construct_mds_product, stac_raw_data)
    return CopernicusMarineCatalogue(
        products=sorted(
            [product for product in products if product],
            key=lambda product: product.product_id,
        )
    )


def _construct_mds_product(
    stac_tuple: Tuple[Collection, list[Item]],
) -> CopernicusMarineProduct:
    stac_product, stac_datasets = stac_tuple
    datasets = map_reject_none(_construct_mds_dataset, stac_datasets)
    production_center = [
        provider.name
        for provider in stac_product.providers
        if "producer" in provider.roles
    ][0]
    return CopernicusMarineProduct(
        title=stac_product.title,
        product_id=stac_product.id,
        thumbnail_url=stac_product.assets["thumbnail"].get_absolute_href(),
        description=stac_product.description,
        production_center=production_center,
        creation_datetime=stac_product.extra_fields["properties"][
            "creationDate"
        ],
        modified_datetime=stac_product.extra_fields["properties"].get(
            "modifiedDate"
        ),
        keywords=stac_product.keywords,
        datasets=sorted(
            [dataset for dataset in datasets],
            key=lambda dataset: dataset.dataset_id,
        ),
    )


def _construct_mds_dataset(
    stac_dataset: Item,
) -> CopernicusMarineProductDataset:
    dataset_id = stac_dataset.id.rsplit("_", maxsplit=1)[
        0
    ]  # Remove the tag e.g.: '_202211'
    return CopernicusMarineProductDataset(
        dataset_id=dataset_id,
        dataset_name=stac_dataset.properties["title"],
        services=_get_services(stac_dataset.get_assets()),
        variables=_get_variables(stac_dataset),
    )


def _get_services(
    stac_assets_dict: dict[str, Asset],
) -> list[CopernicusMarineDatasetService]:

    only_data_stac_assets = [
        CopernicusMarineDatasetService(
            protocol=key,
            uri=value.get_absolute_href(),
        )
        for key, value in stac_assets_dict.items()
        if "data" in value.roles
    ]
    return only_data_stac_assets


def _get_variables(
    stac_dataset: Item,
) -> list[CopernicusMarineDatasetVariable]:
    def _create_variable(
        variable_cube: dict[str, Any],
        bbox: tuple[float, float, float, float],
        coordinates_dict: dict[str, CopernicusMarineDatasetCoordinates],
    ) -> Union[CopernicusMarineDatasetVariable, None]:
        coordinates = variable_cube["dimensions"]
        return CopernicusMarineDatasetVariable(
            short_name=variable_cube["id"],
            standard_name=variable_cube["standardName"],
            units=variable_cube.get("unit") or "",
            bbox=bbox,
            coordinates=[coordinates_dict[key] for key in coordinates],
        )

    coordinates_dict = _get_coordinates(
        stac_dataset.properties["cube:dimensions"]
    )
    bbox = stac_dataset.bbox
    variables: list[Optional[CopernicusMarineDatasetVariable]] = []
    for var_cube in stac_dataset.properties["cube:variables"].values():
        variables += [_create_variable(var_cube, bbox, coordinates_dict)]
    return [var for var in variables if var]


def _get_coordinates(
    dimensions_cube: dict,
) -> dict[str, CopernicusMarineDatasetCoordinates]:
    def _create_coordinate(
        key: str, value: dict
    ) -> CopernicusMarineDatasetCoordinates:
        return CopernicusMarineDatasetCoordinates(
            coordinates_id="depth" if key == "elevation" else key,
            units=value.get("unit") or "",
            minimum_value=value["extent"][0],
            maximum_value=value["extent"][1],
            step=value.get("step"),
            values=value.get("values"),
        )

    coordinates_dict = {}
    for key, value in dimensions_cube.items():
        coordinates_dict[key] = _create_coordinate(key, value)
    return coordinates_dict


# ---------------------------------------
# --- Utils function on any catalogue ---
# ---------------------------------------


def get_protocol_url_from_id(
    dataset_id: str, protocol_key_order: list[str]
) -> Tuple[str, str]:
    catalogue = parse_catalogue()
    dataset_urls = (
        get_dataset_url_from_id(catalogue, dataset_id, protocol)
        for protocol in protocol_key_order
    )
    try:
        dataset_url = next(filter(lambda dataset: dataset, dataset_urls))
        protocol = get_protocol_from_url(dataset_url)
    except StopIteration as exception:
        raise KeyError(
            f"Dataset {dataset_id} does not have a valid protocol "
            f"for subset function. Available protocols: {protocol_key_order}"
        ) from exception
    return protocol, dataset_url


def get_dataset_from_id(
    catalogue: CopernicusMarineCatalogue, dataset_id: str
) -> CopernicusMarineProductDataset:
    for product in catalogue.products:
        for dataset in product.datasets:
            if dataset_id == dataset.dataset_id:
                return dataset
    raise KeyError(
        f"The requested dataset '{dataset_id}' was not found in the catalogue,"
        " you can use 'copernicus-marine describe --include-datasets "
        "-c <search_token>' to find the dataset id"
    )


def get_product_from_url(
    catalogue: CopernicusMarineCatalogue, dataset_url: str
) -> CopernicusMarineProduct:
    """
    Return the product object, with its dataset list filtered
    """
    filtered_catalogue = filter_catalogue_with_strings(
        catalogue, [dataset_url]
    )
    if filtered_catalogue is None:
        raise TypeError("filtered catalogue is empty")
    return filtered_catalogue.products[0]


def get_protocol_from_url(dataset_url) -> str:
    if dataset_url.startswith("ftp://"):
        protocol = FTP_KEY
    elif "/motu-web/Motu" in dataset_url:
        protocol = MOTU_KEY
    elif "/wms/" in dataset_url:
        protocol = "OGC:WMS:getCapabilities"
    elif "/thredds/dodsC/" in dataset_url:
        protocol = OPENDAP_KEY
    elif "/mdl-arco-time/" in dataset_url:
        protocol = TIMECHUNKED_KEY
    elif "/mdl-arco-geo/" in dataset_url:
        protocol = GEOCHUNKED_KEY
    elif "/mdl-native/" in dataset_url:
        protocol = S3NATIVE_KEY
    else:
        raise ValueError(f"No protocol matching url: {dataset_url}")
    return protocol


def get_service_url(
    dataset: CopernicusMarineProductDataset, protocol: str
) -> str:
    service_urls = iter(
        [
            service.uri
            for service in dataset.services
            if service.protocol == protocol
        ]
    )
    return next(service_urls, "")


def get_dataset_url_from_id(
    catalogue: CopernicusMarineCatalogue, dataset_id: str, protocol: str
) -> str:
    dataset = get_dataset_from_id(catalogue, dataset_id)
    return get_service_url(dataset, protocol)


def filter_catalogue_with_strings(
    catalogue: CopernicusMarineCatalogue, tokens: list[str]
) -> Optional[CopernicusMarineCatalogue]:
    filtered_catalogue = deepcopy(catalogue)
    return find_match_object(filtered_catalogue, tokens)


def find_match_object(value: Any, tokens: list[str]) -> Any:
    match: Any
    if isinstance(value, str):
        match = find_match_string(value, tokens)
    elif isinstance(value, list):
        match = find_match_list(value, tokens)
    elif hasattr(value, "__dict__"):
        match = find_match_dict(value, tokens)
    else:
        match = None
    return match


def find_match_string(string: str, tokens: list[str]) -> Optional[str]:
    return string if any(token in string for token in tokens) else None


def find_match_list(object_list: list[Any], tokens) -> Optional[list[Any]]:
    def find_match(element: Any) -> Optional[Any]:
        return find_match_object(element, tokens)

    filtered_list: list[Any] = list(map_reject_none(find_match, object_list))
    return filtered_list if filtered_list else None


def find_match_dict(
    structure: dict[str, Any], tokens
) -> Optional[dict[str, Any]]:
    filtered_dict = {
        key: find_match_object(value, tokens)
        for key, value in structure.__dict__.items()
        if find_match_object(value, tokens)
    }

    found_match = any(filtered_dict.values())
    if found_match:
        new_dict = dict(structure.__dict__, **filtered_dict)
        structure.__dict__ = new_dict
    return structure if found_match else None


def _merge_object(obj1: Any, obj2: Any) -> Any:
    """Function called to merge catalogues
    Redirect either to _merge_list or to _merge_dict functions
    _merge_dict is also used to merge custom_class attributes
    """
    if isinstance(obj1, list):
        return _merge_list(obj1, obj2)
    elif hasattr(obj1, "__dict__"):
        merged_obj = obj1
        merged_obj.__dict__ = _merge_dict(obj1.__dict__, obj2.__dict__)
        return merged_obj
    else:
        return obj1


def _merge_dict(
    dict1: dict[str, Any], dict2: dict[str, Any]
) -> dict[str, Any]:
    """Merge dictionnaries key by key"""
    keys = set(list(dict1.keys()) + list(dict2.keys()))
    return {key: _merge_object(dict1[key], dict2[key]) for key in keys}


def _merge_list(list1: list[Any], list2: list[Any]) -> list[Any]:
    """Merge lists
    If it is a list of one of our custom class, we want to append new objects to list
    and merge matches between the two lists
    Otherwise keep first non-empty list
    """

    def _objects_match(args: Tuple[Any, str, str]) -> Union[Any, None]:
        """Filter to check if an object's attribute match a value"""
        obj, attribute, value = args
        return True if obj.__dict__[attribute] == value else False

    class_id_attribute_dict = {
        CopernicusMarineProduct: "product_id",
        CopernicusMarineProductDataset: "dataset_id",
        CopernicusMarineDatasetService: "protocol",
        CopernicusMarineDatasetVariable: "short_name",
    }
    if not list1:
        if not list2:
            return []
        else:
            main_list = list2
    else:
        main_list = list1
    if isinstance(
        main_list[0],
        (
            CopernicusMarineProduct,
            CopernicusMarineProductDataset,
            CopernicusMarineDatasetService,
            CopernicusMarineDatasetVariable,
        ),
    ):
        id_attribute = class_id_attribute_dict[type(main_list[0])]
        object_ids = set(
            [object1.__dict__[id_attribute] for object1 in list1]
            + [object2.__dict__[id_attribute] for object2 in list2]
        )
        merged_list = []
        for object_id in object_ids:
            list1_match = list(
                filter(
                    _objects_match,
                    zip(
                        list1,
                        [id_attribute] * len(list1),
                        [object_id] * len(list1),
                    ),
                )
            )
            list2_match = list(
                filter(
                    _objects_match,
                    zip(
                        list2,
                        [id_attribute] * len(list2),
                        [object_id] * len(list2),
                    ),
                )
            )
            if list1_match and list2_match:
                merged_list += [
                    _merge_object(list1_match[0][0], list2_match[0][0])
                ]
            elif list1_match:
                merged_list += [list1_match[0][0]]
            elif list2_match:
                merged_list += [list2_match[0][0]]
            else:
                pass
        return sorted(
            merged_list, key=lambda elem: elem.__dict__[id_attribute]
        )
    else:
        return main_list


def merge_catalogues(
    catalogue1: CopernicusMarineCatalogue,
    catalogue2: CopernicusMarineCatalogue,
) -> CopernicusMarineCatalogue:
    """Function to combine two catalogues, with priority given to
    catalogue1 in case of conflicts"""
    catalogue = _merge_object(catalogue1, catalogue2)
    return catalogue


def get_all_dataset_ids() -> list[str]:
    catalogue = parse_catalogue()
    return [
        dataset.dataset_id
        for product in catalogue.products
        for dataset in product.datasets
    ]


if __name__ == "__main__":
    import cProfile
    import io
    import pstats
    from pstats import SortKey

    pr = cProfile.Profile()
    pr.enable()
    parse_catalogue()
    pr.disable()
    s = io.StringIO()
    sortby = SortKey.CUMULATIVE
    ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    ps.print_stats(50)
    print(s.getvalue())
