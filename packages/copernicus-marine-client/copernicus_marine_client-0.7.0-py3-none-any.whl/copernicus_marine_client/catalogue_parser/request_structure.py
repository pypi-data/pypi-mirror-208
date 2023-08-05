from dataclasses import dataclass
from datetime import datetime
from json import load
from typing import Any, Dict, List, Optional


@dataclass
class SubsetRequest:
    dataset_url: Optional[str] = None
    dataset_id: Optional[str] = None
    output_directory: str = ""
    assume_yes: bool = False
    dry_run: bool = False
    variables: Optional[List[str]] = None
    minimal_longitude: Optional[float] = None
    maximal_longitude: Optional[float] = None
    minimal_latitude: Optional[float] = None
    maximal_latitude: Optional[float] = None
    minimal_depth: Optional[float] = None
    maximal_depth: Optional[float] = None
    start_datetime: Optional[datetime] = None
    end_datetime: Optional[datetime] = None
    output_filename: Optional[str] = None
    force_protocol: Optional[str] = None

    def update(self, new_dict: dict):
        """Method to update values in SubsetRequest object.
        Skips "None" values
        """
        for key, value in new_dict.items():
            if value is None or (
                isinstance(value, (list, tuple)) and len(value) < 1
            ):
                pass
            else:
                self.__dict__.update({key: value})

    def enforce_types(self):
        def datetime_parser(string: str):
            for fmt in [
                "%Y",
                "%Y-%m-%d",
                "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%d %H:%M:%S",
            ]:
                try:
                    return datetime.strptime(string, fmt)
                except ValueError:
                    pass
            raise ValueError(f"no valid date format found for: {string}")

        type_enforced_dict = {}
        for key, value in self.__dict__.items():
            if key in [
                "minimal_longitude",
                "maximal_longitude",
                "minimal_latitude",
                "maximal_latitude",
                "minimal_depth",
                "maximal_depth",
            ]:
                new_value = float(value) if value is not None else None
            elif key in [
                "start_datetime",
                "end_datetime",
            ]:
                new_value = datetime_parser(value) if value else None
            elif key in ["assume_yes", "dry_run"]:
                new_value = bool(value) if value is not None else None
            elif key in ["variables"]:
                new_value = list(value) if value is not None else None
            else:
                new_value = str(value) if value else None
            type_enforced_dict[key] = new_value
        self.__dict__.update(type_enforced_dict)

    def from_file(self, filepath: str):
        self.update(subset_request_from_file(filepath).__dict__)
        return self


def subset_request_from_file(filepath) -> SubsetRequest:
    json_file = open(filepath)
    subset_request = SubsetRequest()
    subset_request.__dict__.update(load(json_file))
    subset_request.enforce_types()
    return subset_request


def convert_motu_api_request_to_structure(
    motu_api_request: str,
) -> SubsetRequest:
    prefix = "python -m motuclient "
    string = motu_api_request.replace(prefix, "").replace("'", "")
    arguments = [
        substr.strip() for substr in string.split("--")[1:]
    ]  # for subsubstr in substr.split(" ", maxsplit=1)]
    arg_value_tuples = [
        tuple(substr.split(" ", maxsplit=1)) for substr in arguments
    ]
    motu_api_request_dict: Dict[str, Any] = {}
    for arg, value in arg_value_tuples:
        if arg == "variable":
            # special case for variable, since it can have multiple values
            motu_api_request_dict.setdefault(arg, []).append(value)
        else:
            motu_api_request_dict[arg] = value
    subset_request = SubsetRequest(
        output_directory=".",
        assume_yes=False,
        dry_run=False,
        output_filename=None,
        force_protocol=None,
    )
    conversion_dict = {
        "product-id": "dataset_id",
        "latitude-min": "minimal_latitude",
        "latitude-max": "maximal_latitude",
        "longitude-min": "minimal_longitude",
        "longitude-max": "maximal_longitude",
        "depth-min": "minimal_depth",
        "depth-max": "maximal_depth",
        "date-min": "start_datetime",
        "date-max": "end_datetime",
        "variable": "variables",
    }
    for key, value in motu_api_request_dict.items():
        if key in conversion_dict.keys():
            subset_request.__dict__.update({conversion_dict[key]: value})
    subset_request.enforce_types()
    return subset_request


@dataclass
class NativeRequest:
    dataset_url: Optional[str] = None
    dataset_id: Optional[str] = None
    no_directories: bool = False
    show_outputnames: bool = False
    output_directory: str = "."
    assume_yes: bool = False
    dry_run: bool = False
    force_protocol: Optional[str] = None

    def update(self, new_dict: dict):
        """Method to update values in NativeRequest object.
        Skips "None" values
        """
        for key, value in new_dict.items():
            if value is None:
                pass
            else:
                self.__dict__.update({key: value})

    def enforce_types(self):
        type_enforced_dict = {}
        for key, value in self.__dict__.items():
            if key in [
                "no_directories",
                "show_outputnames",
                "assume_yes",
                "dry_run",
            ]:
                new_value = bool(value) if value is not None else None
            else:
                new_value = str(value) if value else None
            type_enforced_dict[key] = new_value
        self.__dict__.update(type_enforced_dict)

    def from_file(self, filepath: str):
        self = native_request_from_file(filepath)
        print(filepath)
        return self


def native_request_from_file(filepath) -> NativeRequest:
    json_file = open(filepath)
    native_request = NativeRequest()
    native_request.__dict__.update(load(json_file))
    native_request.enforce_types()
    return native_request
