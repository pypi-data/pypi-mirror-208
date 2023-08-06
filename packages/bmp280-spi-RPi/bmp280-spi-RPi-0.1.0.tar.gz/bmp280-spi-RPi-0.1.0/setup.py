from setuptools import setup, find_packages

setup(
    name='bmp280-spi-RPi',
    version='0.1.0',
    author="Michal Tomek",
    description="BMP280 package for Raspberry Pi using SPI interface provided by spidev library",
    long_description="BMP280 package for Raspberry Pi. Provides option for BMP280 configuration and data read. "
                     "Doesn't need linux device tree patch like other BMP280 SPI linux packages. "
                     "Performs raw data processing with calibration data, like specified in BMP280 datasheet. "
                     "Does support single reads, does not support callbacks for fast data sampling yet. ",
    install_requires=[
        'spidev'
    ],
    packages=find_packages(
        include=['bmp280']
    ),
    keywords=["BMP280", "SPI", "RPi", "Raspberry", "Pi"],
    zip_safe=False
)
