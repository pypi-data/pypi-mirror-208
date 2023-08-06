# -*- coding: utf-8 -*-
"""Tests for downloader.py"""
from threedi_scenario_downloader import downloader
import configparser
import os

SCENARIO_UUID = "4d3c9b6d-58d0-43cd-a850-8e6c2982d14f"
SCENARIO_NAME = "threedi-scenario-download-testmodel-EV"
MODEL_UUID = "e5c91df19ad33337d82e8cd83edb1196b7b39d3d"
DEPTH_MAX_UUID = "c3c4dd31-8a15-4a9e-aefa-97d0cb13cbcc"
DEPTH_UUID = "921540af-57aa-4a74-8788-6d8f1c8b518b"


def test_api_key():
    config = configparser.ConfigParser()
    config.read("threedi_scenario_downloader/tests/testdata/realconfig.ini")
    downloader.set_api_key(config["credentials"]["api_key"])

    assert (downloader.get_api_key() is not None) and (
        downloader.get_api_key() == config["credentials"]["api_key"]
    )


def test_download_maximum_waterdepth_raster():
    downloader.download_maximum_waterdepth_raster(
        SCENARIO_UUID,
        "EPSG:28992",
        resolution=1000,
        bbox=None,
        pathname="threedi_scenario_downloader/tests/testdata/max_waterdepth.tif",
    )
    assert os.path.isfile(
        "threedi_scenario_downloader/tests/testdata/max_waterdepth.tif"
    )


def test_download_waterdepth_raster():
    downloader.download_waterdepth_raster(
        SCENARIO_UUID,
        "EPSG:28992",
        1000,
        "2018-06-02T06:00:00Z",
        bbox=None,
        pathname="threedi_scenario_downloader/tests/testdata/waterdepth.tif",
    )
    assert os.path.isfile("threedi_scenario_downloader/tests/testdata/waterdepth.tif")


def test_download_waterdepth_raster_reprojected_bounds():
    bbox = {"east": 115000, "west": 114000, "north": 561000, "south": 560000}
    downloader.download_waterdepth_raster(
        SCENARIO_UUID,
        "EPSG:28992",
        1000,
        "2018-06-02T06:00:00Z",
        bbox=bbox,
        pathname="threedi_scenario_downloader/tests/testdata/waterdepth_reprojected.tif",
    )
    assert os.path.isfile(
        "threedi_scenario_downloader/tests/testdata/waterdepth_reprojected.tif"
    )


def test_download_raw_results():
    downloader.download_raw_results(
        SCENARIO_UUID, "threedi_scenario_downloader/tests/testdata/test.nc"
    )
    assert os.path.isfile("threedi_scenario_downloader/tests/testdata/test.nc")


def test_download_grid_administration():
    downloader.download_grid_administration(
        SCENARIO_UUID, "threedi_scenario_downloader/tests/testdata/test.h5"
    )
    assert os.path.isfile("threedi_scenario_downloader/tests/testdata/test.h5")


def test_get_attachment_links():
    scenario = downloader.find_scenarios_by_name(SCENARIO_NAME)[0]
    links = downloader.get_attachment_links(scenario)
    assert links is not None


def test_rasters_in_scenario():
    scenario = downloader.find_scenarios_by_name(SCENARIO_NAME)[0]
    static_rasters, temporal_rasters = downloader.rasters_in_scenario(scenario)
    assert static_rasters is not None and temporal_rasters is not None


def test_get_raster_download_link():
    raster = downloader.get_raster(SCENARIO_UUID, "depth-max-dtri")
    scenario_instance = downloader.get_scenario_instance(SCENARIO_UUID)
    download_url = downloader.get_raster_download_link(
        raster, scenario_instance, 10, "EPSG:4326", bbox=None, time=None
    )
    assert download_url is not None


def test_download_raster():
    file_path = "threedi_scenario_downloader/tests/testdata/max_wd.tif"

    downloader.download_raster(
        SCENARIO_UUID,
        "depth-max-dtri",
        "EPSG:4326",
        10,
        bbox=None,
        time=None,
        pathname=file_path,
    )
    assert os.path.isfile(file_path)


def test_download_raster_batch():
    scenario_uuids = [SCENARIO_UUID, SCENARIO_UUID]

    file_paths = [
        "threedi_scenario_downloader/tests/testdata/max_wd_batch_1.tif",
        "threedi_scenario_downloader/tests/testdata/max_wd_batch_2.tif",
    ]

    downloader.download_raster(
        scenario_uuids,
        "depth-max-dtri",
        "EPSG:4326",
        10,
        bbox=None,
        time=None,
        pathname=file_paths,
    )

    for file_path in file_paths:
        assert os.path.isfile(file_path)


def test_get_raster_timesteps():
    raster = downloader.get_raster(SCENARIO_UUID, "s1-dtri")
    timesteps = downloader.get_raster_timesteps(raster, interval_hours=None)
    assert isinstance(timesteps, list) and all(
        isinstance(step, str) for step in timesteps
    )


def test_get_raster_from_json():
    scenario_json = downloader.find_scenarios_by_model_slug(MODEL_UUID)[0]
    raster = downloader.get_raster_from_json(scenario_json, "depth-max-dtri")
    assert raster["uuid"] == DEPTH_MAX_UUID


def test_request_json_from_url():
    url = "https://demo.lizard.net/api/v4/scenarios/{}/".format(SCENARIO_UUID)
    assert isinstance(downloader.request_json_from_url(url, params=None), dict)
