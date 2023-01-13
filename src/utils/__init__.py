"""Utilities for Shibbot."""
from datetime import datetime

from .language import factory_language, fl, get_language
from .commands import *
from .re import *


def convert_to_import_path(path: str):
    if path.startswith("/"): path = path[1:]
    elif path.startswith("./"): path = path[2:]
    return path.replace('/', '.')

def relative_timestamp(datetime: datetime) -> str:
    return f"<t:{int(datetime.timestamp())}:R>"

def date_timestamp(datetime: datetime) -> str:
    return f"<t:{int(datetime.timestamp())}:f>"