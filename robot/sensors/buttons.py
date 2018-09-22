try:
    import RPi.GPIO as GPIO
except ImportError:
    import robot.dummyGPIO as GPIO

import enum
import logging

from robot.outputs.leds import LED

logger = logging.getLogger(__name__)


class Button:
    "Parent class for buttons"
    def setup(self):
        pass


class GPIOButton(Button):
    """A GPIO button operates directly on a GPIO pin."""
    def __init__(self, pin, pull_up_down=GPIO.PUD_UP, **kwargs):
        self.pin = pin
        self.pud = pull_up_down

    def setup(self):
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=self.pud)

        GPIO.add_event_detect(self.pin, GPIO.RISING,
                              callback=button_callback, bouncetime=200)


class LEDPushButton(GPIOButton):
    def __init__(self, switch_pin, led_pin, **kwargs):
        super(LEDPushButton, self).__init__(switch_pin, **kwargs)
        self.led = LED(led_pin)

    def setup(self):
        super(LEDPushButton, self).setup()
        self.led.setup()


class ADCButton(Button):
    """A ADCButton is read from the ADC, and we have to
    calculate the threshold manually.
    """
    def __init__(self, adc_pin, **kwargs):
        self.adc_pin = adc_pin


@enum.unique
class ButtonType(str, enum.Enum):
    GPIO = ('gpio_button', GPIOButton)
    LEDPUSH = ('led_push_button', LEDPushButton)
    ADCBUTTON = ('adc_button', ADCButton)

    def __new__(cls, value, button_cls):
        obj = str.__new__(cls)
        obj._value_ = value
        obj.button_cls = button_cls
        return obj

    def __str__(self):
        return self.value


def button_factory(button_def):
    """Create a single button from a button definition."""
    button_type = button_def.pop('type')
    return ButtonType(button_type).button_cls(**button_def)


def multi_button_factory(button_defs):
    """Create a list of buttons from a list of button defs."""
    return [button_factory(x) for x in button_defs]


def button_callback(button_index):
    logger.info(f"Button callback {button_index}")
