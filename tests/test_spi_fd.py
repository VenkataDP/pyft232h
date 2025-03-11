#
# SPI test module, which uses SPI FullDuplex mode
#

import sys, os

sys.path.insert(0, 
                os.path.abspath(os.path.join(os.path.dirname(__file__),
                                             '../src/pyft232h')))
from ft232h import Ft232h_Spi

def main():
    spi_dev = Ft232h_Spi()
    spi_dev.Ft232hSpi_Configure(frequency=2.0E6)
    print ("SPI configured")
    print ("***** without Loopback *****")
    wr_data = bytes([0x41])
    print (f"SPI WRITE: {wr_data}")
    rd_data = spi_dev.spi_write_read(wr_data, len(wr_data))
    print (f"SPI READ data: {rd_data}")
    spi_dev.Ft232hSpi_Loopback(True)
    print ("***** with Loopback *****")
    wr_data = bytes([0x41])
    print (f"SPI WRITE: {wr_data}")
    rd_data = spi_dev.spi_write_read(wr_data, len(wr_data))
    print (f"SPI READ data: {rd_data}")
    spi_dev.Ft232hSpi_Loopback(False)

    return

if __name__ == "__main__":
    main()
