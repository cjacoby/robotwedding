import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)


class LEDPushButton(object):
    def __init__(self, switch_pin, led_pin, pull_up_down=GPIO.PUD_UP):
        self.switch_pin = switch_pin
        self.led_pin = led_pin
        self.pud = pull_up_down
        self.led_state = False

    def setup(self):
        GPIO.setup(self.led_pin, GPIO.OUT)
        GPIO.setup(self.switch_pin, GPIO.IN, pull_up_down=self.pud)

        GPIO.add_event_detect(self.switch_pin, GPIO.RISING,
                              callback=button_callback, bouncetime=200)

    def toggle_led(self):
        print("toggle", self.led_pin)
        if self.led_state is None:
            self.led_state = False
            GPIO.output(self.led_pin, GPIO.LOW)

        self.led_state = not self.led_state
        GPIO.output(self.led_pin, GPIO.HIGH if self.led_state else GPIO.LOW)
        print("LED State (pin", self.led_pin, ") :", self.led_state)


def button_callback(channel):
    print("button", channel)
    if channel in button_switch_map:
        button_switch_map[channel].toggle_led()


buttons = [
    LEDPushButton(18, 4),
    LEDPushButton(27, 17),
    LEDPushButton(23, 22),
    LEDPushButton(25, 24)
]

button_switch_map = {x.switch_pin:x for x in buttons}

if __name__ == "__main__":
    for b in buttons:
        b.setup()

    # Boostrap test
    time.sleep(1)
    for b in buttons:
        b.toggle_led()

    time.sleep(1)
    for b in buttons:
        b.toggle_led()

    message = input("Press enter to quit\n\n")
    GPIO.cleanup()
