import os
import json

"""
底层文件操作
"""

def read_json_from_file(path: str):
    with open(path, "r", encoding="utf-8") as f:
        obj = json.load(f)
    return obj


def read_json_from_file_without_exception(path: str):
    if not os.path.exists(path):
        return None
    return read_json_from_file(path)


def save_as_json(path: str, obj: dict):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False)
