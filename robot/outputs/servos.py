"""Servo controls


FS5103R Ranges:
0 - Stopped
~376/375 - stopped
< 375, > 0: backwards
> 376, -> ~2048

4096 - stopped


"""
import enum
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
    CLIP_MIN = 0.0
    CLIP_MAX = 1.0
    """Servo Controller class."""
    def __init__(self, servo_channel: int,
                 servo_range: tuple = (200, 600)):
        self.channel = servo_channel
        self.servo_range = servo_range
        self.last_value = servo_range[0]

    def setup(self):
        try:
            self.pwm = Adafruit_PCA9685.PCA9685()

            # Set frequency to 60hz, good for servos.
            # ... has to be 60
            self.pwm.set_pwm_freq(60)

            # Initialize it to 0
            self.set_position_norm(0)
        except OSError:
            logger.warning(f"Failed to open Servo/PWM module! (channel={self.channel})")
            self.pwm = None

    @property
    def position(self):
        return self.last_value

    def safe_set_pwm(self, position):
        if self.pwm is not None:
            try:
                self.pwm.set_pwm(self.channel, 0, position)
            except TypeError:
                logger.exception(f"Tried to set servo {self.channel} to {position}")
        else:
            logger.warning("Can't set pwm state - not initialized")

    def set_position(self, value: int):
        """Set the voltage value of the pwm."""
        position_val = int(np.clip(value, *self.servo_range))
        print(f"Servo {self} position: {position_val}")
        self.safe_set_pwm(position_val)
        self.last_value = position_val

    def set_position_norm(self, value: float):
        value = np.clip(value, self.CLIP_MIN, self.CLIP_MAX)
        scaled_value = scale(value, self.servo_range)

        self.set_position(scaled_value)

    def set_position_stepped(self, dest_value: float,
                             time_to_move: float, steps: int = 10,
                             scale_fn=np.linspace):
        scaled_value = scale(dest_value, self.servo_range)
        value_steps = scale_fn(self.last_value, scaled_value, num=steps)
        for v in value_steps:
            self.set_position(v)
            time.sleep(time_to_move / len(step_def))


class ContinuousServo(Servo):
    def __init__(self, servo_channel: int,
                 bw_servo_range: tuple = (375, 4),
                 fw_servo_range: tuple = (2048, 380),
                 stop_value: int = 0):
        self.channel = servo_channel
        self.bw_range = bw_servo_range
        self.fw_range = fw_servo_range
        self.stop_value = stop_value

        self.last_float = 0.0

    @property
    def position(self):
        return self.last_float

    def set_position(self, value: int):
        """Set the voltage value of the pwm."""
        value = int(value)
        print(f"Servo {self} position: {value}")
        self.safe_set_pwm(value)
        self.last_value = value

    def set_position_norm(self, value: float):
        if value == 0 or value < -1 or value > 1:
            self.set_position(0)

        elif value > 0:
            self.set_position(scale(value, self.fw_range))

        elif value < 0:
            value = np.abs(value)
            self.set_position(scale(value, self.bw_range))

        self.last_float = value

    def set_position_stepped(self, dest_value: float,
                             time_to_move: float, steps: int = 10,
                             scale_fn=np.linspace):
        # For this version we scale in norm space
        steps = scale_fn(self.last_float, dest_value, num=steps)
        for step_float in steps:
            self.set_position_norm(step_float)
            time.sleep(time_to_move / steps)


@enum.unique
class ServoType(str, enum.Enum):
    BASIC = ('servo', Servo)
    CONTINUOUS = ('continuous', ContinuousServo)

    def __new__(cls, value, servo_cls):
        obj = str.__new__(cls)
        obj._value_ = value
        obj.servo_cls = servo_cls
        return obj

    def __str__(self):
        return self.value


def servo_factory(servo_defs: list):
    servos = {}

    for s in servo_defs:
        servo_type = s.pop('type')
        servo_label = s.pop('label')
        servos[servo_label] = ServoType(servo_type).servo_cls(**s)

    return servos
