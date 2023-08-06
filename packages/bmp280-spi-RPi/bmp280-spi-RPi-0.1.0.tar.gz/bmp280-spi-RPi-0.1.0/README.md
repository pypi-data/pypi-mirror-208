About
------
BMP280 package for Raspberry Pi. Provides option for BMP280 configuration and data read.
Doesn't need linux device tree patch like other BMP280 SPI linux packages.
Performs raw data processing with calibration data, like specified in BMP280 datasheet.
Does support single reads, does not support callbacks for fast data sampling yet.

Usage
-----
See **example.py** script.

Author
------
Michal Tomek

License
-------
This project is licensed under the MIT license. See the LICENSE.md for details

Contributing
------------
This package was made in just one workday, therefore probably isn't perfect.
Feel free to report issue or make pull request.