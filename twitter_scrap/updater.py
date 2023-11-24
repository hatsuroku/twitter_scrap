from typing import Tuple

from . import decoder
from . import cache_io
from .functional import pipe



def is_entry_eq(a, b):
    return decoder.id_of_entry(a) == decoder.id_of_entry(b)


def find_index_of_last_eq(old, now, key):
    for i, o in enumerate(old):
        for j, n in enumerate(now):
            if key(o) == key(n):
                return j
    return len(now)


class Updater:
    def __init__(self, user_screen_name: str) -> None:
        self.user_screen_name = user_screen_name

    def update(self, instructions: dict) -> None:
        cache_io.save_to_local_instructions(self.user_screen_name, instructions)

    @staticmethod
    def get_new_entries(old_instructions, now_instructions):
        now_pin = decoder.pin_entry_from_instructions(now_instructions)
        now_entries = decoder.entries_from_instructions(now_instructions)

        # 如果没有缓存就直接返回新的
        if old_instructions is None:
            return now_pin, now_entries

        pin = None
        # 有缓存就需要计算出新推文中哪个是已经缓存过了，只留下没缓存的
        old_pin = decoder.pin_entry_from_instructions(old_instructions)
        if old_pin is None:
            if now_pin is not None:
                # 以前没置顶，现在置顶，用新置顶
                pin = now_pin
        else:
            if now_pin is not None and not is_entry_eq(now_pin, old_pin):
                # 有新置顶，需要更新
                pin = now_pin

        old_entries = decoder.entries_from_instructions(old_instructions)
        last_index = find_index_of_last_eq(
            old_entries, now_entries, decoder.id_of_entry
        )

        return pin, now_entries[:last_index]
