#!/usr/bin/env python

"""
Move servos on Servo/PWM Hat.
"""

import click
import logging
import sys
import time

import Adafruit_PCA9685

logging.basicConfig(level=logging.DEBUG)


@click.command()
@click.option('--servo-channel', default=0, help='Servo channel to control.')
@click.option('--servo-min', default=200, help='Min servo pulse length out of 4096.')
@click.option('--servo-max', default=600, help='Max servo pulse length out of 4096.')
def main(servo_channel: int, servo_min: int, servo_max: int) -> None:
    pwm = Adafruit_PCA9685.PCA9685()

    # Set frequency to 60hz, good for servos.
    pwm.set_pwm_freq(60)

    print('Moving servo on channel {0}, press Ctrl-C to quit...'.format(servo_channel))
    while True:
        # Move servo between extremes.
        pwm.set_pwm(servo_channel, 0, servo_min)
        time.sleep(1)
        pwm.set_pwm(servo_channel, 0, servo_max)
        time.sleep(1)


# Helper function to make setting a servo pulse width simpler.
def set_servo_pulse(pwm, channel: int, pulse: int) -> None:
    pulse_length = 1000000    # 1,000,000 us per second
    pulse_length //= 60       # 60 Hz
    print(f'{0}us per period'.format(pulse_length))
    pulse_length //= 4096     # 12 bits of resolution
    print('{0}us per bit'.format(pulse_length))
    pulse *= 1000
    pulse //= pulse_length
    pwm.set_pwm(channel, 0, pulse)


if __name__ == "__main__":
    main()
