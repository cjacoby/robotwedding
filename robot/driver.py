"""The main robot 'driver' lives here."""
import anyconfig
import click
import logging
import numpy as np
import pathlib
import time
from typing import Optional, Mapping, List, Type
from types import TracebackType

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

    def __init__(self, config: Mapping) -> None:
        self.config = config

        self.buttons = buttons.multi_button_factory(
            self.config.get('buttons', []))
        self.leds = [x.led for x in self.buttons
                     if isinstance(x, buttons.LEDPushButton)]
        # self.leds = [False for i in range(self.N_LEDS)]
        self.servos = servos.servo_factory(self.config.get('servos', []))

        self.adc = robot_adc.ADCPoller(**self.config.get('adc'))

        # Clear/reset the callbacks
        self.deregister_callbacks()

        self.displays = robot_display.display_factory(
            self.config.get('display'))

        self.sound = robot_sound.SoundResource()

    def __enter__(self) -> 'RobotDriver':
        self.setup()
        return self

    def __exit__(self,
                 exc_type: Optional[Type[BaseException]] = None,
                 value: Optional[BaseException] = None,
                 traceback: Optional[TracebackType] = None) -> Optional[bool]:
        self.cleanup()

    def __repr__(self) -> str:
        return (f"{self.__class__.__name__}("
                f"n_buttons={len(self.buttons)}, "
                f"n_leds={self.get_n_leds()},"
                f"n_servos={len(self.servos)})")

    def register_button_callback(self, callback):
        self.adc.set_button_callback(callback)

        for button in self.buttons:
            button.register_callback(callback)
            logger.info(f"Button: {button}, {callback}, {button.callback}")

    def register_knob_callback(self, callback):
        self.adc.set_knob_callback(callback)

    def deregister_callbacks(self):
        self.adc.clear_callbacks()

        for button in self.buttons:
            button.clear_callback()

    def get_n_leds(self) -> int:
        return len(self.leds)

    def get_led_state(self, index: int) -> bool:
        return self.leds[index].get_state()

    def toggle_led_state(self, index: int) -> bool:
        self.leds[index].toggle_led()
        return self.leds[index].get_state()

    def toggle_all_leds(self) -> None:
        for b in self.leds:
            b.toggle_led()

    def clear_all_leds(self) -> None:
        for b in self.leds:
            b.set_state(False)
            logger.info(f"Clearing state {b}: {b.led_state}")

    def trigger_button_cb(self, index: int) -> None:
        logger.info(f"Trigger button {index} callback.")

    def set_servo_position(self, index: int, position: float) -> None:
        logger.info(f"Set Servo {index}: {position}")
        if 0 <= index < len(self.servos):
            self.servos[index].set_position_norm(position)

    def set_servo_stepped(self, index: int, position: float,
                          duration: float, steps: int) -> None:
        logger.info(f"Set Servo {index}: {position} over {duration}s")
        if 0 <= index < len(self.servos):
            self.servos[index].set_position_stepped(
                position, duration, steps)

    def read_adc(self) -> np.ndarray:
        return self.adc.poll()

    def read_adc_with_buttons(self) -> np.ndarray:
        adc_vals = self.adc.poll()
        ADC_BUTTON_THRESHOLD = 700
        adc_vals[4:] = adc_vals[4:] * (adc_vals[4:] > ADC_BUTTON_THRESHOLD)
        return adc_vals

    @property
    def display(self) -> Optional[robot_display.OLEDDisplay]:
        if not self.displays:
            return None

        return self.displays[0]

    def setup(self) -> None:
        for b in self.buttons:
            b.setup()
        for s in self.servos:
            s.setup()
        self.adc.setup()
        for d in self.displays:
            d.setup()
        self.sound.setup()

    def cleanup(self) -> None:
        GPIO.cleanup()
