"""The main robot 'driver' lives here."""
import anyconfig
import asyncio
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
        try:
            while True:
                self.adc.poll()
                time.sleep(0.1)
        except KeyboardInterrupt:
            logger.info("Stopping Driver (user cancelled)")

    def run_test_mode(self):
        logger.info("Starting Run Loop")

        runner = TestModeRunner(self)
        runner.run()

    def run_test_async(self):
        logger.info("Starting Run Loop")

        runner = TestAsyncRunner(self)
        runner.run()

    def run_sound_test(self):
        logger.info("Running sound test")
        robot_sound.run_test()

    def run_display_test(self):
        logger.info("Running display test")
        robot_display.run_test()

    def cleanup(self):
        GPIO.cleanup()


class TestModeRunner(object):
    def __init__(self, driver, poll_interval=0.2):
        self.driver = driver
        self.poll_interval = poll_interval

        self.last_display = None

    def run(self):
        while True:
            adc_values = self.driver.read_adc_with_buttons()
            adc_values = adc_values / 1024

            # Split the values in half, and show one per line
            display_text_03 = " ".join(
                [f"{adc_values[i]:1.1f}" for i in range(0, 4)])
            display_text_48 = " ".join(
                [f"{adc_values[i]:1.1f}" for i in range(4, 8)])

            led_state_text = " ".join(
                [f"{l.get_state()}" for l in self.driver.leds])

            servo_state_text = " ".join(
                [f"{s.position}" for s in self.driver.servos])

            display_text = f"ADC:\n{display_text_03}\n{display_text_48}\nLED:\n{led_state_text}\nServos:\n{servo_state_text}"
            if display_text != self.last_display:
                self.driver.display.draw_text(display_text)
                self.last_display = display_text

            logger.debug("Polling Sensors")
            time.sleep(self.poll_interval)


class TestAsyncRunner(object):
    def __init__(self, driver, adc_poll_interval=0.01,
                 display_poll=0.25):
        self.driver = driver
        self.adc_poll_interval = adc_poll_interval
        self.display_poll = display_poll

        self.this_display = None
        self.last_display = None

    def run(self):
        logger.info("Launching async event loop")
        try:
            loop = asyncio.get_event_loop()

            tasks = [
                # asyncio.ensure_future(self.draw_counter()),
                asyncio.ensure_future(self.play_sound()),
                asyncio.ensure_future(self.update_adc()),
                asyncio.ensure_future(self.update_display())
            ]

            loop.run_until_complete(asyncio.wait(tasks))

        finally:
            loop.run_until_complete(loop.shutdown_asyncgens())
            loop.close()
        logger.info("Async event loop complete")

    async def draw_counter(self):
        i = 0
        while True:
            self.driver.display.draw_text(f"{i}")
            await asyncio.sleep(0.5)
            i += 1

    async def play_sound(self):
        freqs = [220, 440, 500, 678, 900, 1223]
        while True:
            await self.driver.sound.aplay_sin(np.random.choice(freqs))
            await asyncio.sleep(2 + np.random.random())

    def set_display_text(self, text):
        self.this_display = text

    async def update_adc(self):
        while True:
            adc_values = self.driver.read_adc_with_buttons()
            adc_values = adc_values / 1024

            # Split the values in half, and show one per line
            display_text_03 = " ".join(
                [f"{adc_values[i]:1.1f}" for i in range(0, 4)])
            display_text_48 = " ".join(
                [f"{adc_values[i]:1.1f}" for i in range(4, 8)])

            led_state_text = " ".join(
                [f"{l.get_state()}" for l in self.driver.leds])

            servo_state_text = " ".join(
                [f"{s.position}" for s in self.driver.servos])

            display_text = f"ADC:\n{display_text_03}\n{display_text_48}\nLED:\n{led_state_text}\nServos:\n{servo_state_text}"
            self.set_display_text(display_text)

            logger.debug("Polling Sensors")
            await asyncio.sleep(self.adc_poll_interval)

    async def update_display(self):
        if self.this_display != self.last_display:
            self.driver.display.draw_text(display_text)
            self.last_display = display_text

        await asyncio.sleep(self.display_poll)

@click.command()
@click.argument('server_mode', type=click.Choice(
                ['osc', 'http', 'standalone', 'ledtest', 'drawtext',
                 'servotest', 'test', 'soundtest', 'screentest', 'asynctest']))
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
        while True:
            time.sleep(0.5)
            driver.toggle_all_leds()

    elif server_mode == "screentest":
        driver.run_display_test()

    elif server_mode == "soundtest":
        driver.run_sound_test()

    elif server_mode == "drawtext":
        try:
            while True:
                text = click.prompt("Text to display (q to quit)")
                if text != 'q':
                    driver.display.draw_text(text)
                else:
                    break

        except KeyboardInterrupt:
            pass

    elif server_mode == "servotest":
        for s in driver.servos:
            s.set_position_norm(0.0)
            time.sleep(0.5)
            s.set_position_norm(1.0)
            time.sleep(0.5)
            s.set_position_norm(0.0)

    elif server_mode == "test":
        driver.run_test_mode()

    elif server_mode == "asynctest":
        driver.run_test_async()

    driver.cleanup()


if __name__ == "__main__":
    run_robot()
