#!/usr/bin/env python
"""
Display text on an OLED screen.
"""
from typing import Mapping, List

import click
import logging
from random import randrange
import textwrap
import time
from PIL import Image
import pathlib

# ignore PIL debug messages
logging.getLogger('PIL').setLevel(logging.ERROR)
logger = logging.getLogger(__name__)

RESOURCES = pathlib.Path(__file__).resolve().parent.parent.parent / "resources"

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

    def clear(self):
        logger.debug("Display clear")
        if self.device is not None:
            self.device.clear()

    def draw_text(self, text):
        logger.debug(f"Drawing: '{text}'")

        if self.echo_result:
            print(text)

        if self.device is not None:
            virtual = viewport(self.device,
                               width=self.device.width,
                               height=self._settings['height'])

            lines = []
            for line in text.split('\n'):
                wrapped_lines = textwrap.wrap(line, self.char_width)
                lines.extend(wrapped_lines)

            with canvas(virtual) as draw:
                for i, line in enumerate(lines):
                    draw.text((0, i * 12), text=line, fill="white")
        else:
            logger.warning(
                f"Cannot draw text - no OLED library found; text={text}")

    def draw_image(self, path, angle=0):
        if self.device is None:
            return

        image = Image.open(path).convert("RGBA")
        image.thumbnail((self.device.width, self.device.height))
        fff = Image.new(image.mode, image.size, (255,) * 4)

        background = Image.new("RGBA", self.device.size, "white")
        posn = ((self.device.width - image.width) // 2, 0)

        rot = image.rotate(angle, resample=Image.BILINEAR)
        img = Image.composite(rot, fff, rot)
        background.paste(img, posn)
        self.device.display(background.convert(self.device.mode))

    def fill_rgb(self, r, g, b):
        if self.device is not None:
            virtual = viewport(self.device,
                               width=self.device.width,
                               height=self._settings['height'])
            with canvas(virtual) as draw:
                draw.rectangle([
                    (0, 0), (self.device.width, self.device.height)],
                    fill=f"rgb({int(r)},{int(g)},{int(b)})")

    def draw_bars(self, param1 : float, param2 : float, margin=5):
        if self.device is None:
            logger.warning(f"Cannot draw - no OLED")
            return

        with canvas(self.device) as draw:
            width = self.device.width
            height = self.device.height

            rect_bottom = height - margin
            rect_max = (rect_bottom - margin)
            rect_left = margin
            rect_right = width - margin

            halfway = (rect_right - rect_left) // 2

            left_rect_height = rect_max * param1
            l_rect_top = rect_max - left_rect_height
            right_rect_height = rect_max * param2
            r_rect_top = rect_max - right_rect_height

            # left rect
            draw.rectangle((rect_left, l_rect_top,
                            halfway, rect_bottom), fill="red")
            # right rect
            draw.rectangle((halfway, r_rect_top,
                            rect_right, rect_bottom), fill="blue")

    def move_and_draw_strs(self):
        def init_stars(num_stars, max_depth):
            stars = []
            for i in range(num_stars):
                # A star is represented as a list with this format: [X,Y,Z]
                star = [randrange(-25, 25), randrange(-25, 25), randrange(1, max_depth)]
                stars.append(star)
            return stars

        origin_x = self.device.width // 2
        origin_y = self.device.height // 2

        if self.device is None:
            logger.warning(f"Cannot draw - no OLED")
            return

        with canvas(self.device) as draw:
            max_depth = 32
            stars = init_stars(512, max_depth)
            for star in stars:
                # The Z component is decreased on each frame.
                star[2] -= 0.19

                # If the star has past the screen (I mean Z<=0) then we
                # reposition it far away from the screen (Z=max_depth)
                # with random X and Y coordinates.
                if star[2] <= 0:
                    star[0] = randrange(-25, 25)
                    star[1] = randrange(-25, 25)
                    star[2] = max_depth

                # Convert the 3D coordinates to 2D using perspective projection.
                k = 128.0 / star[2]
                x = int(star[0] * k + origin_x)
                y = int(star[1] * k + origin_y)

                # Draw the star (if it is visible in the screen).
                # We calculate the size such that distant stars are smaller than
                # closer stars. Similarly, we make sure that distant stars are
                # darker than closer stars. This is done using Linear Interpolation.
                if 0 <= x < self.device.width and 0 <= y < self.device.height:
                    size = (1 - float(star[2]) / max_depth) * 4
                    if (self.device.mode == "RGB"):
                        shade = (int(100 + (1 - float(star[2]) / max_depth) * 155),) * 3
                    else:
                        shade = "white"
                        draw.rectangle((x, y, x + size, y + size), fill=shade)


def display_factory(config: Mapping) -> List[OLEDDisplay]:
    displays = []
    for c in config:
        display_type = c.pop('type')
        if display_type == 'oled':
            displays.append(OLEDDisplay(**c))
    return displays


def run_test():
    oled = OLEDDisplay()
    oled.setup()

    oled.draw_text("This is a test")
    time.sleep(0.3)
    for i in range(15):
        oled.move_and_draw_strs()
        time.sleep(.02)

    time.sleep(0.5)
    oled.draw_image(RESOURCES / "heart1.jpg")
    time.sleep(0.5)
    oled.draw_image(RESOURCES / "heart2.jpg")
    time.sleep(.5)
    oled.fill_rgb(255, 0, 0)
    time.sleep(0.25)
    oled.fill_rgb(255, 0, 0)
    time.sleep(0.25)
    oled.fill_rgb(0, 255, 0)
    time.sleep(0.25)
    oled.fill_rgb(0, 0, 255)


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
