
from enum import IntEnum, unique
import ftd2xx as ftd

class Ft232h_Spi:
    """SPI Master interface for ft232h device"""

    # Data bit positions, refer AN_108-2.1
    SCK_BIT = 0x01
    DO_BIT  = 0x02
    DI_BIT  = 0x04
    CS_BIT  = 0x08

    def __init__(self, debug_trace = False):
        self._ftDev = Ft232h()
        self._frequency     = 6.0E6
        self._base_clk      = 12.0E6
        self._cs_enable     = 0x00
        self._cs_disable    = 0x08
        self._io_direction  = self.CS_BIT | self.DO_BIT | self.SCK_BIT
        self._is_configured = False
        self._wr_code       = self._ftDev.MsbFirst_Cmd.MSB_NVE_OUT_BYTES
        self._rd_code       = self._ftDev.MsbFirst_Cmd.MSB_PVE_IN_BYTES
        self._rw_code       = self._ftDev.MsbFirst_Cmd.MSB_NVE_OUT_PVE_IN_BYTES
        self._trace = debug_trace
    
    def tr_debug(self, _msg, **kwargs):
        if (self._trace == True):
            if (len(kwargs) > 0):
                print(_msg, kwargs)
            else:
                print (_msg)
        return

    def Ft232hSpi_Close(self):
        self._ftDev.close()
        return

    def Ft232hSpi_Configure(self, device: int = 0,
                 frequency: float = 6.0E6
                ) -> None:
        """SPI configuration for ft232h

            * 'frequency' - SPI clock frequency (default 6Mhz)
        """
        # configure the base clock as 60Mhz
        cmd = bytes([self._ftDev.Misc_cmd.DISABLE_CLK_DIV5,
                     self._ftDev.Misc_cmd.DISABLE_ADPTVE_CLK,
                     self._ftDev.Misc_cmd.DISABLE_CLK_3PHASE])
        self._ftDev.write(cmd)
        #self._ftDev.validate_mpsse()
        self._base_clk = 60.0E6
        self.set_frequency(frequency)
        self.spi_csDisable()
        #self._ftDev.validate_mpsse()
        self.tr_debug ("Ft232hSpi configured successfully!!")
        return

    def set_frequency(self, freq) -> None:
        tmp = (self._base_clk/2)
        divisor = int ((tmp/freq) - 1)
        self._frequency = (tmp/(1 + divisor))
        if (freq != self._frequency):
            self.tr_debug (f"{freq/1.0E6}Mhz is not supported!!")
        self.tr_debug (f"Configured frequency: {self._frequency/1.0E6} Mhz")
        # Configure clock divisor
        cmd = bytes([self._ftDev.Misc_cmd.SET_CLK_DIVISOR,
                        (divisor & 0xFF), ((divisor >> 8) & 0xFF)])
        self._ftDev.write(cmd)
        return
    
    def Ft232hSpi_Loopback(self, enable: bool) -> None:
        if (enable == True):
            self._ftDev.loopback_enable()
        else:
            self._ftDev.loopback_disable()
        return
    
    def spi_csEnable(self) -> None:
        cmd = bytes([self._ftDev.DataBits_Cmd.SET_DATA_BITS_LO_BYTE,
                     self._cs_enable,
                     self._io_direction])
        self._ftDev.write(cmd)
        return

    def spi_csDisable(self) -> None:
        cmd = bytes([self._ftDev.DataBits_Cmd.SET_DATA_BITS_LO_BYTE,
                     self._cs_disable,
                     self._io_direction])
        self._ftDev.write(cmd)
        return

    def spi_write(self, wr_data: bytearray, wr_len: int) -> int:
        self.tr_debug (f"SPI WR({wr_len}): {wr_data}")
        self.spi_csEnable()
        cmd = bytes([self._wr_code]) + (wr_len-1).to_bytes(2, 'little')
        cmd = cmd + bytes(wr_data)
        self._ftDev.write(cmd)
        self.spi_csDisable()
        self.tr_debug (f"SPI WR done({wr_len})")
        return wr_len

    def spi_read(self, rd_len: int) -> bytearray:
        read_data = bytearray(7)
        self.tr_debug (f"SPI RD - length({rd_len})")
        self.spi_csEnable()
        cmd = bytes([self._rd_code]) + (rd_len-1).to_bytes(2, 'little')
        self._ftDev.write(cmd)
        self.spi_csDisable()
        read_data = self._ftDev.read(rd_len)
        self.tr_debug (f"SPI RD done({rd_len}): {read_data}")
        return read_data

    def spi_write_read(self, data: bytearray, wr_len) -> bytearray | None:
        self.tr_debug (f"SPI RW: wr_len {wr_len}")
        self.spi_csEnable()
        cmd = bytes([self._rw_code]) + (wr_len - 1).to_bytes(2, 'little')
        cmd = cmd + bytes(data)
        self._ftDev.write(cmd)
        self.spi_csDisable()
        read_data = self._ftDev.read(wr_len)
        self.tr_debug (f"SPI RW done: {read_data}")
        return read_data

class Ft232h:
    """Ft232h driver with MPSSE mode.

    """

    @unique
    class BitMode(IntEnum):
        """Functional Mode selection."""

        RESET = 0x00
        MPSSE = 0x02

    @unique
    class MsbFirst_Cmd(IntEnum):
        """MSB First MPSSE opcodes"""

        MSB_PVE_OUT_BYTES   = 0x10
        MSB_NVE_OUT_BYTES   = 0x11
        MSB_PVE_OUT_BITS    = 0x12
        MSB_NVE_OUT_BITS    = 0x13

        MSB_PVE_IN_BYTES    = 0x20
        MSB_NVE_IN_BYTES    = 0x24
        MSB_PVE_IN_BITS     = 0x22
        MSB_NVE_IN_BITS     = 0x26

        MSB_NVE_OUT_PVE_IN_BYTES   = 0x31
        MSB_PVE_OUT_NVE_IN_BYTES   = 0x34
        MSB_NVE_OUT_PVE_IN_BITS    = 0x33
        MSB_PVE_OUT_NVE_IN_BITS    = 0x36

    @unique
    class DataBits_Cmd(IntEnum):
        """Data bits read/write opcodes"""

        SET_DATA_BITS_LO_BYTE   = 0x80
        SET_DATA_BITS_HI_BYTE   = 0x82
        GET_DATA_BITS_LO_BYTE   = 0x81
        GET_DATA_BITS_HI_BYTE   = 0x83

    @unique
    class Loopback_cmd(IntEnum):
        """Loopback opcodes"""

        # connect DO to DI
        LOOPBACK_ENABLE     = 0x84
        # dis-connect DO to DI
        LOOPBACK_DISABLE    = 0x85

    @unique
    class Misc_cmd(IntEnum):
        """Misc commands"""

        SET_CLK_DIVISOR     = 0x86
        DISABLE_CLK_DIV5    = 0x8a
        ENABLE_CLK_DIV5     = 0x8b
        ENABLE_CLK_3PHASE   = 0x8c
        DISABLE_CLK_3PHASE  = 0x8d
        ENABLE_ADPTVE_CLK   = 0x96
        DISABLE_ADPTVE_CLK  = 0x97

    def __init__(self, latency: int = 16,
                 in_tx_len: int = 65535,
                 out_tx_len: int = 65535,
                 read_timeout: int = 3000,
                 write_timeout: int = 3000,
                 debug_trace: int = False,
                ):
        self._usb_in_tx_size = in_tx_len
        self._usb_out_tx_size = out_tx_len
        self._usb_read_timeout = read_timeout
        self._usb_write_timeout = write_timeout
        self._latency = latency
        self._ftdi = None
        self._trace = debug_trace
        devlist = ftd.listDevices()
        if (devlist is None):
            raise Exception ("No Device Connected")
        devInfo = ftd.getDeviceInfoDetail()
        self.tr_debug (f"Found Device: {devInfo['description'].decode()}")
        self._ftdi = ftd.open()
        self.Enter_MPSSE()

    def tr_debug(self, _msg, **kwargs):
        if (self._trace == True):
            if (len(kwargs) > 0):
                print(_msg, kwargs)
            else:
                print (_msg)
        return

    def Enter_MPSSE(self):
        self.tr_debug ("Enabling MPSSE mode...")
        # reset the device
        self._ftdi.resetDevice()
        self._ftdi.purge()
        # Set USB request transfer size
        self._ftdi.setUSBParameters(self._usb_in_tx_size, self._usb_out_tx_size)
        # Disable event/error charecters
        self._ftdi.setChars(False, 0, False, 0)
        # Set timeouts (ms)
        self._ftdi.setTimeouts(self._usb_read_timeout, self._usb_write_timeout)
        # Set latency timer (ms)
        self._ftdi.setLatencyTimer(self._latency)
        # Reset bit mode
        self._ftdi.setBitMode(0x00, self.BitMode.RESET)
        # Enable MPSSE mode
        self._ftdi.setBitMode(0x00, self.BitMode.MPSSE)
        # check mpsse mode enabled properly or not
        self.sync_mpsse()

    def sync_mpsse(self):
        # enable internal loopback
        self.loopback_enable()
        # check the receive buffer - should be empty
        num_of_bytes_to_read = self._ftdi.getQueueStatus()
        if (num_of_bytes_to_read != 0):
            raise Exception(f"Error: MPSSE receive buffer should be empty")
        self.tr_debug ("Sending dummy command!!")
        dummy_byte = 0xAA
        cmd = bytes([dummy_byte])
        self.write(cmd)
        num_of_bytes_to_read = 0
        # wait for the response
        while(num_of_bytes_to_read == 0):
            num_of_bytes_to_read = self._ftdi.getQueueStatus()
        # read response
        self.tr_debug (f"bytes to read: {num_of_bytes_to_read}")
        readdata = self.read(num_of_bytes_to_read)
        # expect error response and break
        self.tr_debug (f"response: {hex(readdata[0])} {hex(readdata[1])}")
        if (readdata[0] == 0xFA and readdata[1] == dummy_byte):
            self.tr_debug ("Device is insync with MPSSE")
        else:
            raise Exception(f"Fail to sync with MPSSE")
        # disable internal loopback
        self.loopback_disable()
        num_of_bytes_to_read = 0
        # check the receive buffer - should be empty
        num_of_bytes_to_read = self._ftdi.getQueueStatus()
        if (num_of_bytes_to_read != 0):
            raise Exception(f"Error: MPSSE receive buffer should be empty")
        self.tr_debug("MPSSE mode is active!!")
        
    def loopback_enable(self) -> None:
        cmd = bytes([self.Loopback_cmd.LOOPBACK_ENABLE])
        self.write(cmd)
        return
    
    def loopback_disable(self) -> None:
        cmd = bytes([self.Loopback_cmd.LOOPBACK_DISABLE])
        self.write(cmd)
        return

    def validate_mpsse(self) -> None:
        readdata = self.read(2)
        if (len(readdata) >= 2) and (readdata[0] == '\xfa'):
            raise Exception(f"Invalid command!! {readdata[1]}")
        return
    
    def write(self, data: bytearray) -> int:
        """Writes to the device and return num of bytes written"""
        wrLen = 0
        wrLen = self._ftdi.write(data)
        return wrLen
    
    def read(self, rd_len: int) -> bytearray | None:
        """Writes to the device and return num of bytes written"""
        rd_data = bytearray()
        rd_data = self._ftdi.read(rd_len)
        return rd_data
    
    def close(self) -> None:
        """Close the device instance"""
        self._ftdi.close()
        return
