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
import robot.sensors.adc as robot_adc
import robot.outputs.servos as servos
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
            config.get('buttons', []))
        self.leds = [x.led for x in self.buttons
                     if isinstance(x, buttons.LEDPushButton)]
        # self.leds = [False for i in range(self.N_LEDS)]
        # self.knobs_state = [0 for i in range(self.N_KNOBS)]
        self.servos = servos.servo_factory(config.get('servos', []))

        callbacks = [
            robot_adc.LambdaCallback(
                lambda val: self.set_servo_position(0, val / 1024),
                selected_pin=0),
            robot_adc.LambdaCallback(
                lambda val: self.set_servo_position(1, val / 1024),
                selected_pin=1),
            robot_adc.LambdaCallback(
                lambda val: self.set_servo_position(2, val / 1024),
                selected_pin=2),
            robot_adc.LambdaCallback(
                lambda val: self.set_servo_position(3, val / 1024),
                selected_pin=3)
            robot_adc.ButtonCallbackLambda(4,
                lambda: self.toggle_all_leds(); time.sleep(1); self.toggle_all_leds())
        ]
        self.adc = robot_adc.ADCPoller()

    def __repr__(self):
        return f"{self.__class__.__name__}()"

    def get_n_leds(self):
        return len(self.leds)

    def get_led_state(self, index):
        return self.leds[index].get_state()

    def toggle_led_state(self, index):
        self.leds[index].toggle_led()
        return self.leds[index].get_state()

    def toggle_all_leds(self):
        for b in self.leds:
            b.toggle_led()

    def get_knob_state(self, index):
        return self.knobs_state[index]

    def set_knob_state(self, index, value):
        self.knobs_state[index] = value
        return value

    def trigger_button_cb(self, index):
        logger.info(f"Trigger button {index} callback.")

    def set_servo_position(self, index: int, position: float):
        logger.info(f"Set Servo {index}: {position}")
        if 0 <= index < len(self.servos):
            self.servos[index].set_position_norm(position)

    def set_servo_stepped(self, index: int, position: float,
                          duration: float, steps: int):
        logger.info(f"Set Servo {index}: {position} over {duration}s")
        if 0 <= index < len(self.servos):
            self.servos[index].set_position_stepped(
                position, duration, steps)

    def setup(self):
        for b in self.buttons:
            b.setup()
        for s in self.servos:
            s.setup()
        self.adc.setup()

    def run(self):
        logger.info("Running Driver Server")
        try:
            while True:
                self.adc.poll()
                time.sleep(0.1)
        except KeyboardInterrupt:
            logger.info("Stopping Driver (user cancelled)")

    def cleanup(self):
        GPIO.cleanup()


@click.command()
@click.option('-m', '--server_mode', type=click.Choice(
    ['osc', 'http', 'standalone', 'ledtest']))
@click.option('-c', '--config', type=click.Path(exists=True),
              default=default_config)
@click.option('-v', '--verbose', count=True)
def run_robot(server_mode, config, verbose):
    logging.basicConfig(level=logging.DEBUG if verbose else logging.INFO)
    config = anyconfig.load(config, ac_parser="yaml")
    driver = RobotDriver(config)
    driver.setup()

    if server_mode == "osc":
        osc_serve.run_server(driver)

    elif server_mode == "http":
        http_serve.run_server(driver)

    elif server_mode == "standalone":
        driver.run()

    elif server_mode == "ledtest":
        # Boostrap test
        for i in range(6):
            time.sleep(1)
            driver.toggle_all_leds()

    driver.cleanup()


if __name__ == "__main__":
    run_robot()
