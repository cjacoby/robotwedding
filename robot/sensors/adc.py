"""Handle reading data from adc chip.
"""
try:
    import RPi.GPIO as GPIO
except ImportError:
    import robot.dummyGPIO as GPIO

from collections import defaultdict
from typing import Callable, Collection, Mapping, Optional, Sequence
import logging
import numpy as np

logger = logging.getLogger(__name__)


def read_adc_spi_pin(adc_idx, clockpin, mosipin, misopin, cspin):
    """Read the value from a single SPI pin of the MCP3008 chip."""
    if ((adc_idx > 7) or (adc_idx < 0)):
        return -1
    GPIO.output(cspin, True)

    GPIO.output(clockpin, False)  # start clock low
    GPIO.output(cspin, False)     # bring CS low

    commandout = adc_idx
    commandout |= 0x18  # start bit + single-ended bit
    commandout <<= 3    # we only need to send 5 bits here
    for i in range(5):
        if (commandout & 0x80):
            GPIO.output(mosipin, True)
        else:
            GPIO.output(mosipin, False)
        commandout <<= 1
        GPIO.output(clockpin, True)
        GPIO.output(clockpin, False)

    adcout = 0
    # read in one empty bit, one null bit and 10 ADC bits
    for i in range(12):
        GPIO.output(clockpin, True)
        GPIO.output(clockpin, False)
        adcout <<= 1
        if (GPIO.input(misopin)):
            adcout |= 0x1

    GPIO.output(cspin, True)

    adcout >>= 1       # first bit is 'null' so drop it
    return adcout


class ADCKnob(object):
    def __init__(self, pin_index, value, parent):
        self.pin = pin_index
        self.value = value
        self.parent = parent

    def __repr__(self):
        return f"{self.__class__.__name__}(pin={self.pin}, value={self.value}, values={self.parent.last_read})"


class ADCPoller(object):
    """Manage reading data from the MCP3008 ADC chip, using *software SPI*.

    The ADC chip has 8 analog ins.
    """
    N_ANALOG = 8

    def __init__(self,
                 spi_clk: int = 16,
                 spi_miso: int = 19,
                 spi_mosi: int = 20,
                 spi_cs: int = 21,
                 callback_defs: Optional[Mapping[str, str]] = None) -> None:
        self.spi_clk = spi_clk
        self.spi_miso = spi_miso
        self.spi_mosi = spi_mosi
        self.spi_cs = spi_cs

        self.last_read = np.zeros(self.N_ANALOG)
        self.pin_changed = np.zeros(self.N_ANALOG, dtype=bool)
        self.change_tolerance = 5
        self.callback_defs = callback_defs
        self._knob_callback = None
        self._button_callback = None

    def set_knob_callback(self, callback: Callable):
        self._knob_callback = callback

    def set_button_callback(self, callback: Callable):
        self._button_callback = callback

    def clear_callbacks(self):
        self._knob_callback = None
        self._button_callback = None

    def setup(self) -> None:
        # set up the SPI interface pins
        GPIO.setup(self.spi_clk, GPIO.OUT)
        GPIO.setup(self.spi_miso, GPIO.IN)
        GPIO.setup(self.spi_mosi, GPIO.OUT)
        GPIO.setup(self.spi_cs, GPIO.OUT)

    def poll(self) -> np.ndarray:
        """Poll the current ADC values"""
        pin_vals = np.zeros(self.N_ANALOG)
        for pin in range(self.N_ANALOG):
            pin_vals[pin] = read_adc_spi_pin(pin, self.spi_clk,
                                             self.spi_mosi, self.spi_miso,
                                             self.spi_cs)

        for cb_def in self.callback_defs:
            pin = cb_def.get('apin', -1)
            cb_type = cb_def.get('type', 'knob')
            logger.info(f"adc {pin} {cb_type} -")
            if 0 <= pin < 8:
                logger.info(f"adc - 12")
                if cb_type == 'knob' and self._knob_callback:
                    self._knob_callback(self.pin_as_knob(pin))
                elif cb_type == 'button' and self._button_callback:
                    self._button_callback(self.pin_as_button(pin))

        pin_diff = np.abs(pin_vals - self.last_read)
        self.pin_changed = pin_diff > self.change_tolerance
        self.last_read = pin_vals
        return pin_vals

    def pin_as_button(self, pin_index):
        return None

    def pin_as_knob(self, pin_index):
        return ADCKnob(pin_index, self.last_read[pin_index], self)
