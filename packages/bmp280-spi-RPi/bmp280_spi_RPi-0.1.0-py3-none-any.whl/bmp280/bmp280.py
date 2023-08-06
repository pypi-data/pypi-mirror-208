import spidev

_calib_00_addr = 0xA1
_id_addr = 0xD0
_reset_addr = 0xE0
_status_addr = 0xF3
_ctrl_meas_addr = 0xF4
_config_addr = 0xF5
_press_msb_addr = 0xF7


def _get_signed(binary):
    signum = (-1)**(binary >> 15)
    if signum < 0:
        binary = ((binary ^ 0b1111_1111_1111_1111) + 1) * signum
    return binary


def _get_read_address(address):
    return address | 0b1000_0000


def _get_write_address(address):
    return address & 0b0111_1111


class BMP280:
    def __init__(self, spi_bus, spi_dev):
        self._spi = spidev.SpiDev()
        self._spi.open(spi_bus, spi_dev)
        self._spi.mode = 0
        self._spi.max_speed_hz = 10_000_000

        calib = self._read(_get_read_address(0x88), 24)
        self._t1 = calib[0] + (calib[1] << 8)
        self._t2 = _get_signed(calib[2] + (calib[3] << 8))
        self._t3 = _get_signed(calib[4] + (calib[5] << 8))
        self._p1 = calib[6] + (calib[7] << 8)
        self._p2 = _get_signed(calib[8] + (calib[9] << 8))
        self._p3 = _get_signed(calib[10] + (calib[11] << 8))
        self._p4 = _get_signed(calib[12] + (calib[13] << 8))
        self._p5 = _get_signed(calib[14] + (calib[15] << 8))
        self._p6 = _get_signed(calib[16] + (calib[17] << 8))
        self._p7 = _get_signed(calib[18] + (calib[19] << 8))
        self._p8 = _get_signed(calib[20] + (calib[21] << 8))
        self._p9 = _get_signed(calib[22] + (calib[23] << 8))

    def set_spi_max_speed(self, max_speed):
        self._spi.max_speed_hz = max_speed

    def configure(self, temperature_oversamplig, pressure_oversamplig, sampling_interval, filter):
        ctrl_meas_reg = (temperature_oversamplig << 5) + (pressure_oversamplig << 2) + 0b11
        config_reg = (sampling_interval << 5) + (filter << 2) + 0b00
        self._write(_config_addr, config_reg)
        self._write(_ctrl_meas_addr, ctrl_meas_reg)

    def read(self):
        rsp = self._read(_get_read_address(_press_msb_addr), 6)
        raw_p = (rsp[0] << 12) + (rsp[1] << 4) + (rsp[2] >> 4)
        raw_t = (rsp[3] << 12) + (rsp[4] << 4) + (rsp[5] >> 4)

        temp = self._compensate_temperature(raw_t)
        press = self._compensate_pressure(raw_p)

        return {"temp": temp, "press": press}

    def _compensate_temperature(self, adc_t):
        var1 = (adc_t / 16384.0 - self._t1 / 1024.0) * self._t2
        var2 = adc_t / 131072.0 - self._t1 / 8192.0
        var2 = var2 * var2 * self._t3
        self.temperature_fine = (var1 + var2)
        return self.temperature_fine / 5120.0

    def _compensate_pressure(self, adc_p):
        var1 = self.temperature_fine / 2.0 - 64000.0
        var2 = var1 * var1 * self._p6 / 32768.0
        var2 = var2 + var1 * self._p5 * 2
        var2 = var2 / 4.0 + self._p4 * 65536.0
        var1 = (self._p3 * var1 * var1 / 524288.0 + self._p2 * var1) / 524288.0
        var1 = (1.0 + var1 / 32768.0) * self._p1
        pressure = 1048576.0 - adc_p
        pressure = (pressure - var2 / 4096.0) * 6250.0 / var1
        var1 = self._p9 * pressure * pressure / 2147483648.0
        var2 = pressure * self._p8 / 32768.0
        return pressure + (var1 + var2 + self._p7) / 16.0

    def _write(self, address, data):
        self._spi.xfer([_get_write_address(address), data])

    def _read(self, address, count):
        tb = (0x80, ) * count
        tb = (_get_read_address(address),) + tb
        rb = self._spi.xfer(tb)
        return rb[1:]
