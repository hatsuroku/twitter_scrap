from functional import pipe
import decoder
from decoder import name_id_map
from fetch import fetch
import cache_io
from updater import Updater


class TweetGetter:
    def __init__(self, user_screen_name: str) -> None:
        self.user_screen_name = user_screen_name
        self.updater = Updater(user_screen_name)

    def _fetch_new_instructions(self):
        return pipe(
            name_id_map.get,
            fetch.fetch_twitter_obj,
            decoder.instructions_from_UserTweet_api_obj,
        )(self.user_screen_name)

    # 获取新推特，并且更新到本地
    def get_and_update(self, do_update=True):
        old_instructions = cache_io.read_local_instructions(self.user_screen_name)
        now_instructions = self._fetch_new_instructions()
        pin, entries = self.updater.get_new_entries(old_instructions, now_instructions)
        ret = decoder.timeline_from_entries(pin, entries)
        if do_update:
            self.updater.update(now_instructions)
        return ret

    # 只获取新推特，不更新到本地
    def get(self):
        return self.get_and_update(do_update=False)
