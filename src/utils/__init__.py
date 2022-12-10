"""Utilities for Shibbot."""
import datetime

from .json import *
from .logger import Logger
from .system import ServerSpecifications, auto_gc_clear
from .reddit import Reddit
from .language import factory_language, fl, get_language
from .commands import *


def relative_timestamp(datetime: datetime.datetime) -> str:
    return f"<t:{int(datetime.timestamp())}:R>"

def date_timestamp(datetime: datetime.datetime) -> str:
    return f"<t:{int(datetime.timestamp())}:f>"