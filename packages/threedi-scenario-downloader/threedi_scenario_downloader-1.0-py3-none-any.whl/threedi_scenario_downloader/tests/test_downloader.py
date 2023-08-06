# -*- coding: utf-8 -*-
"""Tests for downloader.py"""
from threedi_scenario_downloader import downloader
import configparser
import pytest
from requests.exceptions import HTTPError


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


def test_find_scenario():
    r1 = downloader.find_scenarios(name__icontains=SCENARIO_NAME, limit=100)
    assert r1[0]["uuid"] == SCENARIO_UUID


def test_find_scenario_by_model_slug():
    r = downloader.find_scenarios_by_model_slug(MODEL_UUID)
    assert r[0]["uuid"] == SCENARIO_UUID


def test_get_netcdf_link():
    url = downloader.get_netcdf_link(SCENARIO_UUID)
    assert (
        url == "https://demo.lizard.net/api/v4/scenario-results/210501/results_3di.nc"
    )


def test_get_raster():
    raster = downloader.get_raster(SCENARIO_UUID, "depth-max-dtri")
    print(raster)
    assert raster["uuid"] == DEPTH_MAX_UUID


def test_get_raster_temporal():
    raster = downloader.get_raster(SCENARIO_UUID, "depth-dtri")
    assert raster["uuid"] == DEPTH_UUID


def test_get_raster_url_from_non_existing_scenario():
    with pytest.raises(HTTPError):
        raster = downloader.get_raster(
            "3d3c9b6d-58d0-43cd-a850-8e6c2982d14f", "depth-max-dtri"
        )
        assert raster is not None


def test_create_raster_task():
    task = downloader.create_raster_task(
        downloader.get_raster(SCENARIO_UUID, "depth-max-dtri"),
        downloader.get_scenario_instance(SCENARIO_UUID),
        projection="EPSG:28992",
    )
    assert task is not None
