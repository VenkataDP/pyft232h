# pyft232h

python based SPI driver for ft232h using mpsse mode. 


## Pre-Requisites

**ftd2xx** package must be installed. 
ftd2xx shall be installed using below command
> pip install ftd2xx


## Version Log

### ***V1.0.0***

1. SPI write/read with Half/Full duplex support using MPSSE
2. SPI MODE 0 alone is supported


## BUILD and INSTALL

This package can be build and installed locally.

### ***build the package***

> python -m build

### ***install package locally***

Install locally
> python setup.py install --user


## TESTS

tests directory has sample files to test the SPI over ft232h

### ***test_spi_fd.py***

This test file uses SPI full duplex mode. enables write and read both at a time.
> python tests/test_spi_fd.py

### ***test_spi_hd.py***

This test file uses SPI half duplex mode. Use write/read once at a time.
> python tests/test_spi_hd.py
