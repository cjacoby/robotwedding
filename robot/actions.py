"""
'Script' methods which list actions for the robot.
Each script takes the driver as a parameter.
Each should also be a coroutine.
"""
import abc
import asyncio
import logging
logger = logging.getLogger(__name__)

registry = {}


class Action(abc.ABC):
    def __init__(self, driver):
        self.driver = driver

    @classmethod
    def __init_subclass__(cls, **kwargs):
        global registry
        super().__init_subclass__(**kwargs)

        registry[cls.__name__] = cls


class BasicTest(Action):
    async def run(self):
        logger.info("action_test - wait")
        await asyncio.sleep(1)


class ActionPlayTwoSounds(Action):
    def button_callback(self, button):
        pass

    def knob_callback(self, knob):
        pass

    async def run(self):
        await self.driver.sound.aplay_init_sound()
        await self.driver.sound.aplay_speech("Hello, I am the robot")

        await self.driver.sound.aplay_sin(freq=1000, dur=1)

        await self.driver.sound.aplay_init_sound()
