import pytest

import robot.sensors.buttons as buttons


@pytest.mark.parametrize('button_def,expected', [
    ({"type": "gpio_button",
      "pin": 22},
     buttons.GPIOButton),
    ({"type": "led_push_button",
      "switch_pin": 22,
      "led_pin": 23},
     buttons.LEDPushButton),
    ({"type": "adc_button",
      "adc_pin": 0},
     buttons.ADCButton),
])
def test_button_factory(button_def, expected):
    button = buttons.button_factory(button_def)
    assert isinstance(button, buttons.Button)
    assert isinstance(button, expected)


def test_multi_button_factory():
    defs = [
        {"type": "gpio_button",
         "pin": 22},
        {"type": "led_push_button",
         "switch_pin": 22,
         "led_pin": 23},
        {"type": "adc_button",
         "adc_pin": 0}
    ]

    result = buttons.multi_button_factory(defs)

    assert isinstance(result[0], buttons.GPIOButton)
    assert isinstance(result[1], buttons.LEDPushButton)
    assert isinstance(result[2], buttons.ADCButton)


@pytest.mark.parametrize('button_type,expected', [
    ("gpio_button", buttons.GPIOButton),
    ("led_push_button", buttons.LEDPushButton),
    ("adc_button", buttons.ADCButton),
])
def test_buttontype_enum(button_type, expected):
    b = buttons.ButtonType(button_type)
    assert b.button_cls == expected
    assert button_type == str(b)
