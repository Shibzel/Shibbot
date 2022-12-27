import time
import struct
import base64

from src import database as db, remove_chars


last_id = None

def get_unique_id() -> str:
    """Should return a safe enough unique ID."""
    global last_id
    last_id = unique_id = "".join([letter if letter != "=" else "" for letter in remove_chars(base64.encodebytes(struct.pack('<d', time.time())).decode('utf-8'), "=\n")])
    return get_unique_id() if unique_id == last_id else unique_id