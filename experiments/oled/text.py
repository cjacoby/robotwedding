#!/usr/bin/env python

"""
Display text on the screen.
"""

import argparse
import time
import sys
import logging

import luma.core
from luma.core import cmdline, error
from luma.core.virtual import viewport
from luma.core.render import canvas

logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)-15s - %(message)s'
    )
# ignore PIL debug messages
logging.getLogger('PIL').setLevel(logging.ERROR)


def parse_args():
    actual_args = sys.argv[1:]
    
    parser = cmdline.create_parser(description="Display text on display.")

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
        iface = f"Interface: {args.interface}\n"
        
    lib_name = cmdline.get_library_for_display_type(args.display)
    if lib_name is not None:
        lib_version = cmdline.get_library_version(lib_name)
    else:
        lib_name = lib_version = "unknown"

    version = f"luma.{lib_name} {lib_version} (luma.core {luma.core.__version__})"
    
    return f"Version: {version}\nDisplay: {args.display}\n{iface}Dimensions: {args.width} x {args.height}"


def main(args):
    virtual = viewport(args.device, width=args.device.width, height=args.height)

    with canvas(virtual) as draw:
        draw.text((0, 0), "Text on the screen")

    input("Please Enter to close")


if __name__ == "__main__":
    try:
        main(parse_args())
    except KeyboardInterrupt:
        pass
