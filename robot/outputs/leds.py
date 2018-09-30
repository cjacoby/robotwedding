try:
    import RPi.GPIO as GPIO
except ImportError:
    import robot.dummyGPIO as GPIO
import logging

logger = logging.getLogger(__name__)


class LED(object):
    def __init__(self, led_pin: int) -> None:
        self.led_pin: int = led_pin
        self.led_state: bool = False

    def setup(self) -> None:
        GPIO.setup(self.led_pin, GPIO.OUT)
        self.set_state(self.led_state)

    def toggle_led(self) -> None:
        logger.debug(f"LED Toggle {self.led_pin}")
        if self.led_state is None:
            self.led_state = False
            GPIO.output(self.led_pin, GPIO.LOW)

        self.led_state = not self.led_state
        self.set_state(self.led_state)

    def set_state(self, state: bool) -> None:
        GPIO.output(self.led_pin, GPIO.HIGH if self.led_state else GPIO.LOW)
        logger.debug("LED State (pin %i) : %i", self.led_pin, self.led_state)

    def get_state(self) -> bool:
        return self.led_state
