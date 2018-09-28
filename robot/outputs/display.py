#!/usr/bin/env python
"""
Display text on an OLED screen.
"""
import click
import logging
import textwrap


# ignore PIL debug messages
logging.getLogger('PIL').setLevel(logging.ERROR)
logger = logging.getLogger(__name__)

try:
    from luma.core.render import canvas
    from luma.core.virtual import viewport
except ImportError:
    logger.error("No luma display libraries located")
    luma = None


class OLEDDisplay(object):
    _settings = {'backlight_active': 'low',
                 'bgr': False,
                 'block_orientation': 0,
                 'config': 'oled.config',
                 'display': 'ssd1351',
                 'framebuffer': 'diff_to_previous',
                 'gpio': None,
                 'gpio_backlight': 18,
                 'gpio_data_command': 5,
                 'gpio_mode': None,
                 'gpio_reset': 6,
                 'h_offset': 0,
                 'height': 128,
                 'i2c_address': '0x3C',
                 'i2c_port': 1,
                 'interface': 'spi',
                 'mode': 'RGB',
                 'rotate': 0,
                 'spi_bus_speed': 8000000,
                 'spi_cs_high': False,
                 'spi_device': 0,
                 'spi_port': 0,
                 'spi_transfer_size': 4096,
                 'text': "hello i'm a screen",
                 'v_offset': 0,
                 'width': 128}

    def __init__(self, echo_result=True, **kwargs):
        self.echo_result = echo_result
        self._settings.update(**kwargs)

    def setup(self):
        try:
            import luma.oled.device
            Device = getattr(luma.oled.device, self._settings['display'])
            self.device = Device(OLEDDisplay.make_spi(self._settings),
                                 **self._settings)

            self.char_width = int(self._settings['width'] / 6)
        except ImportError:
            self.device = None
            self.char_width = None

    @staticmethod
    def make_spi(settings):
        from luma.core.interface.serial import spi

        return spi(port=settings['spi_port'],
                   device=settings['spi_device'],
                   bus_speed_hz=settings['spi_bus_speed'],
                   cs_high=settings['spi_cs_high'],
                   transfer_size=settings['spi_transfer_size'],
                   gpio_DC=settings['gpio_data_command'],
                   gpio_RST=settings['gpio_reset'],
                   gpio=None)

    def draw_text(self, text):
        logger.debug(f"Drawing: '{text}'")

        lines = []
        for line in text.split('\n'):
            wrapped_lines = textwrap.wrap(text, self.char_width)
            lines.extend(wrapped_lines)

        if self.echo_result:
            print(text)

        if self.device is not None:
            virtual = viewport(self.device,
                               width=self.device.width,
                               height=self._settings['height'])

            with canvas(virtual) as draw:
                for i, line in enumerate(lines):
                    draw.text((0, i * 12), text=line, fill="white")
        else:
            logger.warning(
                f"Cannot draw text - no OLED library found; text={text}")


def display_factory(config):
    displays = []
    for c in config:
        display_type = c.pop('type')
        if display_type == 'oled':
            displays.append(OLEDDisplay(**c))
    return displays


@click.command()
@click.option('--text')
def main(text):
    if not text:
        print("No text to display.")
        return

    oled = OLEDDisplay()
    oled.setup()

    oled.draw_text(text)

    input("Please Enter to close")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
