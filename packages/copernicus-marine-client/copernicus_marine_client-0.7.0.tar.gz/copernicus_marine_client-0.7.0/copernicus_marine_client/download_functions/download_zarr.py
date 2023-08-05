from datetime import datetime
from os import path
from typing import List, Optional, Tuple

import click
import numpy as np
import xarray as xr
import zarr

from copernicus_marine_client.catalogue_parser.request_structure import (
    SubsetRequest,
)


def subset(
    ds,
    variables: Optional[List[str]] = None,
    geographical_subset: Optional[
        Tuple[
            Optional[float], Optional[float], Optional[float], Optional[float]
        ]
    ] = None,
    temporal_subset: Optional[
        Tuple[Optional[datetime], Optional[datetime]]
    ] = None,
    depth_range: Optional[Tuple[Optional[float], Optional[float]]] = None,
) -> xr.Dataset:

    if variables:
        ds = ds[np.array(variables)]

    if geographical_subset:
        (
            minimal_latitude,
            maximal_latitude,
            minimal_longitude,
            maximal_longitude,
        ) = geographical_subset
        if ("latitude" in ds.coords) and any(geographical_subset):
            ds = ds.sel(
                latitude=slice(minimal_latitude, maximal_latitude),
                longitude=slice(minimal_longitude, maximal_longitude),
            )
        elif ("nav_lat" in ds.coords) and any(geographical_subset):
            mask = (
                (ds.nav_lon > minimal_longitude)
                & (ds.nav_lon < maximal_longitude)
                & (ds.nav_lat > minimal_latitude)
                & (ds.nav_lat < maximal_latitude)
            )
            geoindex = np.argwhere(mask.values)
            xmin = min(geoindex[:, 1])
            xmax = max(geoindex[:, 1])
            ymin = min(geoindex[:, 0])
            ymax = max(geoindex[:, 0])

            ds = ds.isel(
                x=slice(xmin, xmax),
                y=slice(ymin, ymax),
            )
        else:
            ds = ds.sel(
                lat=slice(minimal_latitude, maximal_latitude),
                lon=slice(minimal_longitude, maximal_longitude),
            )

    if temporal_subset:
        (start_datetime, end_datetime) = temporal_subset
        if "time_counter" in ds.coords:
            ds = ds.sel(time_counter=slice(start_datetime, end_datetime))
        else:
            ds = ds.sel(time=slice(start_datetime, end_datetime))

    if (("depth" in ds.dims) or ("deptht" in ds.dims)) and (
        depth_range is not None and any(depth_range)
    ):
        (
            minimal_depth,
            maximal_depth,
        ) = depth_range
        if "deptht" in ds.dims:
            ds = ds.sel(deptht=slice(minimal_depth, maximal_depth))
        else:
            ds = ds.sel(depth=slice(minimal_depth, maximal_depth))
    elif ("elevation" in ds.dims) and (
        depth_range is not None and any(depth_range)
    ):
        (
            minimal_depth,
            maximal_depth,
        ) = depth_range
        minimal_depth = minimal_depth * -1.0 if minimal_depth else None
        maximal_depth = maximal_depth * -1.0 if maximal_depth else None
        ds = ds.sel(elevation=slice(maximal_depth, minimal_depth))

    return ds


def get_optimized_chunking(subset_request: SubsetRequest) -> str:
    """Function to calculate the optimized type of chunking,
    based on a subset_request.
    Returns a str: "map" if time-chunking is optimized,
    "timeserie" if geo-chunking is optimized
    """
    print(
        "WARNING: THIS CHUNKING OPTIMIZATION FUNCTION IS "
        + "A PLACEHOLDER, DO NOT RELY ON IT!!"
    )
    chunking_selected = "map"
    if (
        isinstance(subset_request.minimal_latitude, float)
        and isinstance(subset_request.maximal_latitude, float)
        and isinstance(subset_request.minimal_longitude, float)
        and isinstance(subset_request.maximal_longitude, float)
    ):
        surface = abs(
            subset_request.maximal_longitude - subset_request.minimal_longitude
        ) * abs(
            subset_request.maximal_latitude - subset_request.minimal_latitude
        )

        if surface < 20:
            chunking_selected = "timeserie"
    return chunking_selected


def download_dataset(
    login: str,
    password: str,
    geographical_subset: Optional[
        tuple[
            Optional[float], Optional[float], Optional[float], Optional[float]
        ]
    ],
    temporal_subset: Optional[tuple[Optional[datetime], Optional[datetime]]],
    depth_range: Optional[tuple[Optional[float], Optional[float]]],
    dataset_url: str,
    output_directory: str,
    output_filename: str,
    variables: Optional[list[str]],
    assume_yes: bool = False,
):

    dataset = xr.open_zarr(dataset_url)
    dataset = subset(
        dataset, variables, geographical_subset, temporal_subset, depth_range
    )

    if not assume_yes:
        print(dataset)
        click.confirm("Do you want to continue?", abort=True, default=True)

    store = zarr.DirectoryStore(path.join(output_directory, output_filename))
    dataset.to_zarr(store)


def download_zarr(
    login: str,
    password: str,
    subset_request: SubsetRequest,
):

    geographical_subset = (
        subset_request.minimal_latitude,
        subset_request.maximal_latitude,
        subset_request.minimal_longitude,
        subset_request.maximal_longitude,
    )
    temporal_subset = (
        subset_request.start_datetime,
        subset_request.end_datetime,
    )
    depth_range = (subset_request.minimal_depth, subset_request.maximal_depth)
    dataset_url = str(subset_request.dataset_url)
    output_directory = (
        subset_request.output_directory
        if subset_request.output_directory
        else "."
    )
    output_filename = (
        subset_request.output_filename
        if subset_request.output_filename
        else "data.zarr"
    )
    variables = subset_request.variables
    assume_yes = subset_request.assume_yes

    download_dataset(
        login=login,
        password=password,
        geographical_subset=geographical_subset,
        temporal_subset=temporal_subset,
        depth_range=depth_range,
        dataset_url=dataset_url,
        output_directory=output_directory,
        output_filename=output_filename,
        variables=variables,
        assume_yes=assume_yes,
    )
    return path.join(output_directory, output_filename)
