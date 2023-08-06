Changelog of threedi-scenario-downloader
===================================================

1.0 (2023-05-15)
----------------

- Changed functions to support the Lizard API v4 (v3 is not supported with this release)
- Added error statements for faulty API requests


0.16 (2022-09-07)
-----------------

- Added ``find_scenarios_by_exact_name()`` function that doesn't do a case
  insensitive search for names *containing* the search term (like
  ``find_scenarios_by_name()`` does), but only does an exact match. Handy if
  there are too many similarly-named scenarios.


0.15 (2021-08-12)
-----------------

- Bump bleach to 3.1.4


0.14 (2021-08-12)
-----------------

- Added download aggregation NetCDF function

- Added download logging function

- Added function descriptions

- Minor fixes


0.13 (2021-07-22)
-----------------

- Added batch functionality to raster download

- Added resume batch function


0.12 (2020-02-18)
-----------------

- Adaptation for improved feedback from Lizard API task endpoint


0.11 (2019-06-03)
-----------------

- Updated find_scenarios method. Use 'name' argument for exact searches and 'name__icontains' for partial searches


0.10 (2019-05-27)
-----------------

- Increased download chunk size

- Added bounds_srs as optional argument to define the spatial reference system the bounds are supplied in


0.9 (2019-05-22)
----------------

- Updated download method using stream

- Updated urllib3 dependency


0.8 (2019-03-14)
----------------

- Bugfix in downloading total damage rasters


0.7 (2019-02-15)
----------------

- Added temporal rasters with interval

- Retrieve grouped (static, temporal) download links from scenario


0.6 (2019-02-13)
----------------

- Added method for downloading raw 3Di result

- Added method for downloading gridadmin

- Added authentication method for downloading files from Lizard API


0.5 (2019-02-13)
----------------

- Cleanup of docstrings and usage of request parameters

- Make result-limit changable

- Added url retrieval methods

- Added editable result limit on searches


0.2 (2019-01-24)
----------------

- Added automatic deploys to https://pypi.org/project/threedi-scenario-downloader/

0.1 (2019-01-23)
----------------

- Initial project structure created with cookiecutter and https://github.com/nens/cookiecutter-python-template

- Initial working version.
