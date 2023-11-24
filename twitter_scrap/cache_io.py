import os
from . import file
from .decoder import name_id_map

CACHE_DIR = "cache"
CACHE_PATH = os.path.join(os.getcwd(), CACHE_DIR)

"""
twitter cache IO 操作
"""


def ensure_cache_exist():
    if not os.path.exists(CACHE_PATH):
        os.makedirs(CACHE_PATH)


def twitter_filename_from_user(user_screen_name: str):
    return os.path.join(
        CACHE_PATH, f"{user_screen_name}---{name_id_map.get(user_screen_name)}.json"
    )


def read_local_instructions(user_screen_name: str):
    ensure_cache_exist()
    return file.read_json_from_file_without_exception(twitter_filename_from_user(user_screen_name))


def save_to_local_instructions(user_screen_name: str, instructions: dict):
    ensure_cache_exist()
    file.save_as_json(twitter_filename_from_user(user_screen_name), instructions)
