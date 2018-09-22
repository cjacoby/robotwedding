"""Servo controls
"""
import numpy as np
import logging
import time

import Adafruit_PCA9685

logger = logging.getLogger(__name__)


def scale(value, range_):
    """
    Arguments
    ---------
    value : float [0, 1]
    range : tuple (min, max)
    """
    return (value * (range_[1] - range_[0]) + range_[0])


class Servo(object):
    """Servo Controller class."""
    def __init__(self, servo_channel: int,
                 servo_range: tuple = (200, 600)):
        self.channel = servo_channel
        self.servo_range = servo_range
        self.last_value = servo_range[0]

    def setup(self):
        self.pwm = Adafruit_PCA9685.PCA9685()

        # Set frequency to 60hz, good for servos.
        # ... has to be 60
        self.pwm.set_pwm_freq(60)

    def set_position(self, value: int):
        """Set the voltage value of the pwm."""
        position_val = int(np.clip(value, *self.servo_range))
        print(f"Servo {self} position: {position_val}")
        self.pwm.set_pwm(self.channel, 0, position_val)
        self.last_value = value

    def set_position_norm(self, value: float):
        value = np.clip(value, 0.0, 1.0)
        scaled_value = scale(value, self.servo_range)
        self.set_position(scaled_value)

    def set_position_stepped(self, dest_value: float,
                             time_to_move: float, steps: int = 10,
                             scale_fn=np.linspace):
        dest_value = np.clip(dest_value, 0.0, 1.0)
        scaled_value = scale(dest_value, self.servo_range)
        value_steps = scale_fn(self.last_value, scaled_value, num=steps)

        for v in value_steps:
            self.set_position(v)
            time.sleep(time_to_move / steps)


def servo_factory(servo_defs : list):
    return [Servo(**x) for x in servo_defs]
