import os
import json

"""
底层文件操作
"""


def read_json_from_file(path: str):
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as twitter_file:
        obj = json.load(twitter_file)
    return obj


def save_as_json(path: str, obj: dict):
    with open(path, "w", encoding="utf-8") as twitter_file:
        json.dump(obj, twitter_file, ensure_ascii=False)
