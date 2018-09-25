"""Handle reading data from adc chip.
"""
try:
    import RPi.GPIO as GPIO
except ImportError:
    import robot.dummyGPIO as GPIO

from collections import defaultdict
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


class ADCCallback(object):
    def on_poll(self, pin_vals):
        raise NotImplementedError()

    def on_pin_changed(self, pin_vals):
        raise NotImplementedError()

    def on_rise(self, pin_vals, pin_changed):
        raise NotImplementedError()


class LambdaCallback(ADCCallback):
    def __init__(self, poll_lam=None, selected_pin=None):
        self.poll_lam = poll_lam
        self.selected_pin = selected_pin

    def on_poll(self, pin_vals):
        if self.poll_lam is not None:
            value = (pin_vals[self.selected_pin] if self.selected_pin
                     else pin_vals)
            self.poll_lam(value)


class ButtonCallback(ADCCallback):
    """Trigger on_rise when the threshold changes."""
    def __init__(self, selected_pin, on_threshold=900):
        self.selected_pin = selected_pin
        self.on_threshold = on_threshold

    def on_rise(self):
        """Triggered when the callback is executed."""
        raise NotImplementedError()


class ButtonCallbackLambda(ButtonCallback):
    def __init__(self, selected_pin, btn_lam, on_threshold=900):
        super(ButtonCallbackLambda, self).__init__(
            selected_pin, on_threshold)
        self.btn_lam = btn_lam

    def on_rise(self):
        self.btn_lam()


class ADCCallbackList(object):
    """Container abstracting a list of callbacks."""
    def __init__(self, callbacks=None):
        callbacks = callbacks or []
        self.callbacks = [c for c in callbacks]

    def append(self, callback):
        self.callbacks.append(callback)

    def __iter__(self):
        return iter(self.callbacks)

    def on_poll(self, pin_vals):
        logger.debug(f"on_poll() : {pin_vals}")
        for callback in self.callbacks:
            callback.on_poll(pin_vals)

    def on_rise(self, pin_vals, pin_changed):
        for callback in self.callbacks:
            if (hasattr(callback, 'selected_pin') and
                    hasattr(callback, 'on_threshold')):
                pin_index = callback.selected_pin
                if (pin_vals[pin_index] > callback.on_threshold and
                        self.pin_changed):
                    callback.on_rise()


class ADCPoller(object):
    """Manage reading data from the MCP3008 ADC chip, using *software SPI*.

    The ADC chip has 8 analog ins.
    """
    N_ANALOG = 8

    def __init__(self, spi_clk=16, spi_miso=19,
                 spi_mosi=20, spi_cs=21,
                 callbacks=None):
        self.spi_clk = spi_clk
        self.spi_miso = spi_miso
        self.spi_mosi = spi_mosi
        self.spi_cs = spi_cs

        self.last_read = np.zeros(self.N_ANALOG)
        self.pin_changed = np.zeros(self.N_ANALOG, dtype=bool)
        self.change_tolerance = 5
        self.set_callbacks(callbacks)

    def set_callbacks(self, callbacks):
        _callbacks = callbacks or []
        self.callbacks = ADCCallbackList(_callbacks)

    def setup(self):
        # set up the SPI interface pins
        GPIO.setup(self.spi_clk, GPIO.OUT)
        GPIO.setup(self.spi_miso, GPIO.IN)
        GPIO.setup(self.spi_mosi, GPIO.OUT)
        GPIO.setup(self.spi_cs, GPIO.OUT)

    def poll(self):
        """Poll the current ADC values"""
        pin_vals = np.zeros(self.N_ANALOG)
        for pin in range(self.N_ANALOG):
            pin_vals[pin] = read_adc_spi_pin(pin, self.spi_clk,
                                             self.spi_mosi, self.spi_miso,
                                             self.spi_cs)
        self.callbacks.on_poll(pin_vals)

        pin_diff = np.abs(pin_vals - self.last_read)
        self.pin_changed = pin_diff > self.change_tolerance

        self.callbacks.on_rise(pin_vals, self.pin_changed)

        self.last_read = pin_vals
        return pin_vals
