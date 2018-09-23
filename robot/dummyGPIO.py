"""For mocking GPIO calls for testing on a PC."""
import logging

logger = logging.getLogger(__name__)

PUD_UP = "foo"
RISING = None
OUT = None
IN = None
HIGH = 1
LOW = 0
BCM = None


def setmode(mode):
    pass


def setwarnings(*args, **kwargs):
    pass


def setup(*args, **kwargs):
    pass


def add_event_detect(*args, **kwargs):
    pass


def output(*args, **kwargs):
    pass


def cleanup():
    pass
