import asyncio
import enum
import logging
import time
import numpy as np
from queue import Queue

logger = logging.getLogger(__name__)


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
            self.driver.display.draw_text(self.this_display)
            self.last_display = self.this_display

        await asyncio.sleep(self.display_poll)


@enum.unique
class RobotStates(enum.Enum):
    DEFAULT = 0
    BEEP_BOOP = 1
    WHIMSICAL_TASKS = 2
    POLL_QA = 3
    RANDOM_FACTOIDS = 4


class RobotStateMachineRunner(object):
    """Class which manages the main event loop of the 'real' robot mode.
    """
    def __init__(self, driver):
        self.driver = driver
        self.current_state = RobotStates.DEFAULT
        self.state_change_event = asyncio.Event()

    def run(self):
        logger.info("Beggining State Machine")
        try:
            loop = asyncio.get_event_loop()

            tasks = [
                asyncio.ensure_future(self.run_state_machine_controller()),
                asyncio.ensure_future(self.random_state_changes())
            ]

            loop.run_until_complete(asyncio.wait(tasks))

        finally:
            loop.run_until_complete(loop.shutdown_asyncgens())
            loop.close()
        logger.info("Async event loop complete")

    async def run_state_machine_controller(self):
        while True:
            logger.info("Back to sleep")
            await self.state_change_event.wait()
            logger.info(f"State change! {self.current_state}")
            self.state_change_event.clear()

    async def random_state_changes(self):
        while True:
            # Wait some random number of seconds
            sleep_time = np.random.random() + 3
            logger.info(f"State change sleep time: {sleep_time}")
            await asyncio.sleep(sleep_time)

            # Set a new state
            self.current_state = np.random.randint(5)

            logger.info(f"Set: {self.current_state}")
            self.state_change_event.set()
            logger.info(f"Set: {self.current_state}")
