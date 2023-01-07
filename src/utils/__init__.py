"""Utilities for Shibbot."""
import datetime

from .json import *
from .logger import Logger, PStyles
from .hardware import ServerSpecifications, auto_gc, Uptime
from .reddit import Reddit
from .language import factory_language, fl, get_language
from .commands import *
from .re import *


def convert_to_import_path(path: str):
    if path.startswith("/"): path = path[1:]
    elif path.startswith("./"): path = path[2:]
    return path.replace('/', '.')

def relative_timestamp(datetime: datetime.datetime) -> str:
    return f"<t:{int(datetime.timestamp())}:R>"

def date_timestamp(datetime: datetime.datetime) -> str:
    return f"<t:{int(datetime.timestamp())}:f>"