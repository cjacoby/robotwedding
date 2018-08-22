#!/usr/bin/env python

"""
Display text on the screen.
"""

import argparse
import logging
import sys
import textwrap
import time

#import classify
import camera.rpi

import luma.core
from luma.core import cmdline, error
from luma.core.render import canvas
from luma.core.virtual import viewport

logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)-15s - %(message)s'
    )
# ignore PIL debug messages
logging.getLogger('PIL').setLevel(logging.ERROR)


def parse_args():
    actual_args = sys.argv[1:]

    parser = cmdline.create_parser(description="Display text on display.")
    parser.add_argument(
        "--text",
        type=str,
        default="Text on the screen!",
        help="Text to display on screen.")

    args = parser.parse_args()

    if args.config:
        # load config from file
        config = cmdline.load_config(args.config)
        args = parser.parse_args(config + actual_args)

    print(args)
    print(display_settings(args))
    print('-' * 60)

    try:
        args.device = cmdline.create_device(args)
    except error.Error as e:
        parser.error(e)

    return args


def display_settings(args):
    """
    Display a short summary of the settings.
    :rtype: str
    """
    iface = ""
    display_types = cmdline.get_display_types()
    if args.display not in display_types["emulator"]:
        iface = "Interface: "

    lib_name = cmdline.get_library_for_display_type(args.display)
    if lib_name is not None:
        lib_version = cmdline.get_library_version(lib_name)
    else:
        lib_name = lib_version = "unknown"

    version = ""

    return ""


def main(args):
    if not args.text:
        print("No text to display.")
        return

    img_gen = camera.rpi.generate_capture()
    image = next(img_gen)
    img_gen.close()

    import classify

    classification = classify.classify_image(image)

    char_width = int(args.width / 6)
    lines = textwrap.wrap(classification, char_width)

    virtual = viewport(args.device, width=args.device.width, height=args.height)

    with canvas(virtual) as draw:
        for i, line in enumerate(lines):
            draw.text((0, i * 12), text=line, fill="white")

    input("Please Enter to close")


if __name__ == "__main__":
    try:
        main(parse_args())
    except KeyboardInterrupt:
        pass
