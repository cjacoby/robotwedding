"""The main robot 'driver' lives here."""
import anyconfig
import click
import logging
import pathlib
import time

try:
    import RPi.GPIO as GPIO
except ImportError:
    import robot.dummyGPIO as GPIO

import robot.sensors.buttons as buttons
import robot.servers.osc as osc_serve
import robot.servers.http as http_serve

logger = logging.getLogger(__name__)

default_config = (pathlib.Path(__file__).parent.parent / "config" /
                  "config.yaml")

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)


class RobotDriver:
    N_LEDS = 4
    N_BUTTONS = 8
    N_KNOBS = 4

    def __init__(self, config):
        self.buttons = buttons.multi_button_factory(
            config['buttons'])
        self.leds = [x.led for x in self.buttons
                     if isinstance(x, buttons.LEDPushButton)]
        # self.leds = [False for i in range(self.N_LEDS)]
        # self.knobs_state = [0 for i in range(self.N_KNOBS)]

    def __repr__(self):
        return f"{self.__class__.__name__}()"

    def get_n_leds(self):
        return len(self.leds)

    def get_led_state(self, index):
        return self.leds[index].get_state()

    def toggle_led_state(self, index):
        self.leds[index].toggle_led()
        return self.leds[index].get_state()

    def get_knob_state(self, index):
        return self.knobs_state[index]

    def set_knob_state(self, index, value):
        self.knobs_state[index] = value
        return value

    def trigger_button_cb(self, index):
        logger.info(f"Trigger button {index} callback.")

    def setup(self):
        for b in self.buttons:
            b.setup()

    def cleanup(self):
        GPIO.cleanup()


@click.command()
@click.option('-m', '--server_mode', type=click.Choice(
    ['osc', 'http', 'standalone', 'ledtest']))
@click.option('-c', '--config', type=click.Path(exists=True),
              default=default_config)
def run_robot(server_mode, config):
    config = anyconfig.load(config, ac_parser="yaml")
    driver = RobotDriver(config)
    driver.setup()

    if server_mode == "osc":
        osc_serve.run_server(driver)

    elif server_mode == "http":
        http_serve.run_server(driver)

    elif server_mode == "standalone":
        message = input("Press enter to quit\n\n")

    elif server_mode == "ledtest":
        # Boostrap test
        for i in range(6):
            time.sleep(1)
            for b in driver.leds:
                b.toggle_led()

    driver.cleanup()


if __name__ == "__main__":
    run_robot()
