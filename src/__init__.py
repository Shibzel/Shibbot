from os import path as __path, makedirs as __makedirs

from .constants import *

__title__ = "Shibbot"
__author__ = "Shibzel"
__version__ = "1.0.0"
__license__ = "GPL-3.0"
__copyright__ = "Copyright (c) 2022 Shibzel"
__github__ = "https://github.com/Shibzel/Shibbot"

folders_to_create = (LOGS_PATH, CACHE_PATH, EXTENSIONS_PATH)
for dir in folders_to_create:
    if not __path.exists(dir):
        __makedirs(dir)
