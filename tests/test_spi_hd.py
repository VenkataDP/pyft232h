#
# SPI test module, which uses SPI HalfDuplex mode
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
    wr_data = bytes([0x41])
    print (f"SPI WRITE: {wr_data}")
    wr_len = spi_dev.spi_write(wr_data, len(wr_data))
    if (wr_len != len(wr_data)):
        print (f"written only {wr_len} out of {len(wr_data)}")
        return
    rd_len = 1
    print (f"SPI READ len: {rd_len}")
    rd_data = spi_dev.spi_read(rd_len)
    print (f"SPI READ data: {rd_data}")
    return

if __name__ == "__main__":
    main()
