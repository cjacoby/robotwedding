"""The main robot 'driver' lives here."""
import click
import logging

import robot.servers.osc as osc_serve
import robot.servers.http as http_serve

logger = logging.getLogger(__name__)


class RobotDriver:
    N_LEDS = 4
    N_BUTTONS = 8
    N_KNOBS = 4

    def __init__(self):
        self.leds = [False for i in range(self.N_LEDS)]
        self.button_cb = []
        self.knobs_state = [0 for i in range(self.N_KNOBS)]

    def __repr__(self):
        return f"{self.__class__.__name__}()"

    def get_n_leds(self):
        return len(self.leds)

    def get_led_state(self, index):
        return self.leds[index]

    def toggle_led_state(self, index):
        self.leds[index] = not self.leds[index]
        return self.leds[index]

    def get_knob_state(self, index):
        return self.knobs_state[index]

    def set_knob_state(self, index, value):
        self.knobs_state[index] = value
        return value

    def trigger_button_cb(self, index):
        logger.info(f"Trigger button {index} callback.")


@click.command()
@click.option('-m', '--server_mode', type=click.Choice(['osc', 'http']))
def run_robot(server_mode):
    driver = RobotDriver()

    if server_mode == "osc":
        osc_serve.run_server(driver)

    elif server_mode == "http":
        http_serve.run_server(driver)


if __name__ == "__main__":
    run_robot()
