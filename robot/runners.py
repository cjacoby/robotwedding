import asyncio
import enum
import logging
import random
import time
import numpy as np
from typing import Callable
from queue import Queue

import robot.actions

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


class RobotScriptRunner(object):
    """Class which manages the main event loop of the 'real' robot mode.
    """
    def __init__(self, driver, adc_poll_interval=0.05):
        self.driver = driver
        self.adc_poll_interval = adc_poll_interval

    def _get_main_loop(self) -> robot.actions.Action:
        return robot.actions.MainLoop

    def _get_random_action(self) -> robot.actions.Action:
        return random.choice(list(robot.actions.registry.values()))

    def run(self) -> None:
        logger.info("Beggining State Machine")
        try:
            loop = asyncio.get_event_loop()

            tasks = [
                asyncio.ensure_future(self.poll_adc()),
                asyncio.ensure_future(self.run_action_loop()),
            ]

            loop.run_until_complete(asyncio.wait(tasks))

        finally:
            loop.run_until_complete(loop.shutdown_asyncgens())
            loop.close()
        logger.info("Async event loopf complete")

    async def poll_adc(self) -> None:
        while True:
            logger.debug("Polling Sensors")
            adc_values = self.driver.read_adc_with_buttons()
            logger.debug(f"ADC Values: {adc_values}")
            # adc_values = adc_values / 1024
            await asyncio.sleep(self.adc_poll_interval)

    async def run_action_loop(self) -> None:
        logger.info("Beginning action loop")
        action_queue = []

        while True:
            if len(action_queue) == 0:
                logger.info("Going to main loop")
                action_queue.append(self._get_main_loop())

            action = action_queue.pop(0)(self.driver)
            logger.info(f"Action chosen: {action}")
            logger.info(f"Remaining Actions: {len(action_queue)}")

            # Activates the callbacks
            with action:
                new_actions = await action.run()

                if new_actions is not None and isinstance(new_actions, list):
                    action_queue.extend(new_actions)
                elif new_actions is not None:
                    action_queue.append(new_actions)
