"""
'Script' methods which list actions for the robot.
Each script takes the driver as a parameter.
Each should also be a coroutine.
"""
import abc
import asyncio
import collections
import logging

from robot.outputs.display import RESOURCES

logger = logging.getLogger(__name__)

registry = {}
tagged_registry = collections.defaultdict(list)


class Action(abc.ABC):
    tags = []

    def __init__(self, driver):
        self.driver = driver

    @classmethod
    def __init_subclass__(cls, **kwargs):
        global registry
        super().__init_subclass__(**kwargs)

        registry[cls.__name__] = cls

        for tag in cls.tags:
            tagged_registry[tag].append(cls)

    def __enter__(self):
        "register the subclass's callbacks, if available, to the driver"
        logger.info(f"__enter__")
        if hasattr(self, 'button_callback'):
            logger.info(f"__enter__ {self.button_callback}")
            self.driver.register_button_callback(self.button_callback)

        if hasattr(self, 'knob_callback'):
            logger.info(f"__enter__ {self.knob_callback}")
            self.driver.register_knob_callback(self.knob_callback)

        return self

    def __exit__(self, *exec):
        "deregister callbacks"
        logger.info(f"Degregistering {self}'s callbacks")
        self.driver.deregister_callbacks()
        return False


class MainLoop(Action):
    def __init__(self, driver, sleep_time=15):
        super(MainLoop, self).__init__(driver)
        self.next_state = None
        self.sleep_time = 30

        self.bar_one = 0.4
        self.bar_two = 0.8

    def button_callback(self, button):
        logger.info(f"Button Callback {button}")
        if button is not None and hasattr(button, 'label') and hasattr(button, 'led') and button.led.get_state():
            self.next_state = button.label

    def knob_callback(self, knob):
        logger.debug(f"Knob callback {knob}")
        if knob.pin == 2:
            self.bar_one = 1 - (knob.value / 1024)
        elif knob.pin == 3:
            self.bar_two = 1 - (knob.value / 1024)
        logger.debug(f"Knob callback {knob}; {self.bar_one} {self.bar_two}")

    async def run(self):
        result = None
        total_sleep = 0
        logger.info("MainLoop")
        self.driver.display.draw_text("Hello! Main loop.")
        self.driver.display.draw_bars(self.bar_one, self.bar_two)
        await self.driver.sound.aplay_speech("Hello.")
        await self.driver.sound.aplay_speech(
            "Welcome to Christopher and Zo ell's wedding")
        while total_sleep < self.sleep_time:
            logger.debug(f"Next loop - {total_sleep}, {self.next_state}")
            if self.next_state is not None:
                self.driver.display.draw_text(f"Pushed {self.next_state}")
                await self.driver.sound.aplay_speech(f"You pushed {self.next_state}")
                await asyncio.sleep(0.25)

                if self.next_state == "red":
                    result = FlashStuff
                    break
                elif self.next_state == "blue":
                    result = ActionPlayTwoSounds
                    break
                elif self.next_state == "green":
                    result = WeddingIsLoading
                    break
                elif self.next_state == "yellow":
                    result = DanceParty
                    break
                else:
                    self.driver.clear_all_leds()
                self.next_state = None

            self.driver.display.draw_bars(self.bar_one, self.bar_two)
            await asyncio.sleep(.1)
            total_sleep += .1

        self.driver.display.clear()
        self.driver.clear_all_leds()
        return result


class FlashStuff(Action):
    tags = ['random']

    async def run(self):
        logger.info("FlashStuff")
        self.driver.display.draw_text("beep beep!")
        await asyncio.sleep(0.5)
        for i in range(6):
            logger.info(f"FlashStuff - {i}")
            self.driver.toggle_all_leds()
            self.driver.display.fill_rgb(255 * (i / 6), 0, 0)
            await asyncio.sleep(0.25)
            self.driver.toggle_all_leds()
            await asyncio.sleep(0.25)
        self.driver.display.clear()

        return MainLoop


class BasicTest(Action):
    async def run(self):
        logger.info("action_test - wait")
        await asyncio.sleep(1)


class ActionPlayTwoSounds(Action):
    def button_callback(self, button):
        logger.debug(f"ActionPlayTwoSounds Button callback: {knob}")

    def knob_callback(self, knob):
        logger.debug("Knob callback:", knob)

    async def run(self):
        self.driver.display.draw_image(RESOURCES / "heart1.jpg")
        await self.driver.sound.aplay_init_sound()
        await self.driver.sound.aplay_speech("Hello, I am the robot")

        await self.driver.sound.aplay_sin(freq=1000, dur=1)
        self.driver.display.draw_image(RESOURCES / "heart2.jpg")

        await self.driver.sound.aplay_init_sound()


class ActionPrintKnobCallback(Action):
    def knob_callback(self, knob):
        logger.debug("Knob callback:", knob)

    async def run(self):
        await asyncio.sleep(1)


class WeddingIsLoading(Action):
    async def run(self):
        await self.driver.sound.aplay_init_sound()
        await self.driver.sound.aplay_speech("Thank you for using our service. Your wedding is generating")
        self.driver.display.draw_image(RESOURCES / "4_B_wedding-generating-1.png")
        await asyncio.sleep(1)
        self.driver.display.draw_image(RESOURCES / "4_B_wedding-generating-2.png")
        await asyncio.sleep(1)
        self.driver.display.draw_image(RESOURCES / "4_B_wedding-generating-3.png")
        await asyncio.sleep(1)
        self.driver.display.draw_image(RESOURCES / "4_B_wedding-generating-4.png")
        await asyncio.sleep(1)


class DanceParty(Action):
    tags = ['random']

    async def run(self):
        await self.driver.sound.aplay_sin(freq=400, dur=.2)
        await self.driver.sound.aplay_sin(freq=800, dur=.2)
        await self.driver.sound.aplay_sin(freq=400, dur=.2)
        await self.driver.sound.aplay_sin(freq=800, dur=.2)
