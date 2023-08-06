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
    print(config["credentials"]["api_key"])
    downloader.set_api_key(config["credentials"]["api_key"])

    assert (downloader.get_api_key() is not None) and (
        downloader.get_api_key() == config["credentials"]["api_key"]
    )


def test_download_raster_batch():
    scenario_uuids = [SCENARIO_UUID, SCENARIO_UUID]

    file_paths = [
        "threedi_scenario_downloader/tests/testdata/max_wd_batch_1.tif",
        "threedi_scenario_downloader/tests/testdata/max_wd_batch_2.tif",
    ]

    export_task_csv = "threedi_scenario_downloader/tests/testdata/batch.csv"

    downloader.download_raster(
        scenario_uuids,
        "depth-max-dtri",
        "EPSG:4326",
        10,
        bbox=None,
        time=None,
        pathname=file_paths,
        export_task_csv=export_task_csv,
    )

    for file_path in file_paths:
        assert os.path.isfile(file_path)
