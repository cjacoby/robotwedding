try:
    import RPi.GPIO as GPIO
except ImportError:
    import robot.dummyGPIO as GPIO
import logging

logger = logging.getLogger(__name__)


class LED(object):
    def __init__(self, led_pin):
        self.led_pin = led_pin
        self.led_state = False

    def setup(self):
        GPIO.setup(self.led_pin, GPIO.OUT)

    def toggle_led(self):
        logger.debug(f"LED Toggle {self.led_pin}")
        if self.led_state is None:
            self.led_state = False
            GPIO.output(self.led_pin, GPIO.LOW)

        self.led_state = not self.led_state
        GPIO.output(self.led_pin, GPIO.HIGH if self.led_state else GPIO.LOW)
        logger.debug("LED State (pin", self.led_pin, ") :", self.led_state)

    def get_state(self):
        return self.led_state
