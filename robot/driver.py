"""The main robot 'driver' lives here."""
import anyconfig
import click
import logging
import numpy as np
import pathlib
import time

try:
    import RPi.GPIO as GPIO
except ImportError:
    import robot.dummyGPIO as GPIO

import robot.sensors.buttons as buttons
import robot.sensors.adc as robot_adc
import robot.outputs.display as robot_display
import robot.outputs.servos as servos
import robot.outputs.sound as robot_sound
import robot.servers.osc as osc_serve
import robot.servers.http as http_serve
import robot.runners as robot_runners

logger = logging.getLogger(__name__)

default_config = (pathlib.Path(__file__).parent.parent / "config" /
                  "config.yaml")

np.set_printoptions(suppress=True)
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
        self.servos = servos.servo_factory(config.get('servos', []))

        def toggle_leds():
            self.toggle_all_leds()
            time.sleep(1)
            self.toggle_all_leds()

        callbacks = [
            # robot_adc.LambdaCallback(
            #     lambda val: self.set_servo_position(0, val / 1024),
            #     selected_pin=0),
            robot_adc.LambdaCallback(
                lambda val: self.set_servo_position(1, val / 1024),
                selected_pin=1),
            robot_adc.LambdaCallback(
                lambda val: self.set_servo_position(2, val / 1024),
                selected_pin=2),
            robot_adc.LambdaCallback(
                lambda val: self.set_servo_position(3, val / 1024),
                selected_pin=3),
            # robot_adc.ButtonCallbackLambda(4, toggle_leds)
        ]
        self.adc = robot_adc.ADCPoller()
        self.adc.set_callbacks(callbacks)

        self.displays = robot_display.display_factory(
            config.get('display'))

        self.sound = robot_sound.SoundResource()

    def __repr__(self):
        return (f"{self.__class__.__name__}("
                f"n_buttons={len(self.buttons)}, "
                f"n_leds={self.get_n_leds()},"
                f"n_servos={len(self.servos)})")

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

    def read_adc(self):
        return self.adc.poll()

    def read_adc_with_buttons(self):
        adc_vals = self.adc.poll()
        ADC_BUTTON_THRESHOLD = 700
        adc_vals[4:] = adc_vals[4:] * (adc_vals[4:] > ADC_BUTTON_THRESHOLD)
        return adc_vals

    @property
    def display(self):
        if self.displays:
            return self.displays[0]

    def setup(self):
        for b in self.buttons:
            b.setup()
        for s in self.servos:
            s.setup()
        self.adc.setup()
        for d in self.displays:
            d.setup()
        self.sound.setup()

    def run(self):
        logger.info("Running Driver Server")
        runner = robot_runners.RobotStateMachineRunner(self)
        try:
            runner.run()
        except KeyboardInterrupt:
            logger.info("Stopping Driver (user cancelled)")

    def run_http_server(self):
        http_serve.run_server(self)

    def run_test_mode(self):
        logger.info("Starting Run Loop")

        runner = robot_runners.TestModeRunner(self)
        runner.run()

    def run_async_test(self):
        logger.info("Starting Run Loop")

        runner = robot_runners.TestAsyncRunner(self)
        runner.run()

    def run_led_test(self):
        # Boostrap test
        while True:
            time.sleep(0.5)
            self.toggle_all_leds()

    def run_text_test(self):
        try:
            while True:
                text = click.prompt("Text to display (q to quit)")
                if text != 'q':
                    self.display.draw_text(text)
                else:
                    break

        except KeyboardInterrupt:
            pass

    def run_servo_test(self):
        logger.info("Servo Test")
        for s in self.servos:
            s.set_position_norm(0.0)
            time.sleep(0.5)
            s.set_position_norm(1.0)
            time.sleep(0.5)
            s.set_position_norm(0.0)

    def run_sound_test(self):
        logger.info("Running sound test")
        robot_sound.run_test()

    def run_display_test(self):
        logger.info("Running display test")
        robot_display.run_test()

    def cleanup(self):
        GPIO.cleanup()


driver_modes = {
    'osc': None,
    'http': 'run_http_server',
    'run': 'run',
    'ledtest': 'run_led_test',
    'screentest': 'run_display_test',
    'soundtest': 'run_sound_test',
    'drawtext': 'run_text_test',
    'servotest': 'run_servo_test',
    'test': 'run_test_mode',
    'asynctest': 'run_async_test'
}


@click.command()
@click.argument('server_mode', type=click.Choice(driver_modes.keys()))
@click.option('-c', '--config', type=click.Path(exists=True),
              default=default_config)
@click.option('-v', '--verbose', count=True)
def run_robot(server_mode, config, verbose):
    logging.basicConfig(level=logging.DEBUG if verbose else logging.INFO)
    config = anyconfig.load(config, ac_parser="yaml")
    driver = RobotDriver(config)
    driver.setup()

    run_fn = getattr(driver, driver_modes[server_mode])
    run_fn()

    driver.cleanup()


if __name__ == "__main__":
    run_robot()
