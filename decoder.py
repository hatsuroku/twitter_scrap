import file
from fetch import fetch
import os
from typing import Optional
from datetime import datetime
from functional import pipe
from tweet import Tweet, Timeline, build_twitter_url

"""
从 Twitter API 返回的数据中解析出 user_id
"""


def id_from_UserByScreenName_api_obj(obj: dict) -> str:
    try:
        user_id = obj["data"]["user"]["result"]["rest_id"]
    except KeyError as e:
        raise KeyError(
            "UserByScreenName 接口返回失败，输入的用户名可以有误，或者 json 结构有更改"
        ).with_traceback(e.__traceback__)
    return user_id


"""
在解析 Twitter API 返回的数据的过程中，如果找不到对应的 key，就抛出异常
"""


def parse_UserTweet_decorator(parse_func):
    def inner1(*args, **kwargs):
        try:
            ret = parse_func(args[0])
        except KeyError as e:
            raise KeyError("UserTweet 接口返回失败，输入的内容可能有误，或者 json 结构有更改").with_traceback(
                e.__traceback__
            )
        return ret

    return inner1


"""
Tweet 和 Timeline 相关，把提取的字段转为用户可操作的数据
"""


def timeline_from_entries(pin_entry=None, entries=None):
    return Timeline(
        None if pin_entry is None else tweet_from_entry(pin_entry),
        None if entries is None else [tweet_from_entry(entry) for entry in entries],
    )


def tweet_from_entry(entry: dict) -> Tweet:
    return pipe(info_from_entry, tweet_from_info)(entry)


def info_from_entry(entry: dict) -> dict:
    return pipe(_result_from_entry, _info_from_result)(entry)


def tweet_from_info(info: dict) -> Tweet:
    return Tweet(
        user_id=info["user_id"],
        user_screen_name=info["user_screen_name"],
        user_name=info["user_name"],
        user_profile_image=info["user_profile_image"],
        id_str=info["id_str"],
        full_text=info["full_text"],
        created_time=info["created_time"],
        created_time_epoch=info["created_time_epoch"],
        media_url_list=info["media_url_list"],
        retweet_src=info["retweet_src"],
        quote_src=info["quote_src"],
    )


"""
从 Twitter API 返回的数据提取关键字段

instructions 是一个列表，没置顶的用户长度为 2，有置顶的长度为 3
如果有置顶则置顶推文为 instruction[1]，普通推文在 instruction[2]
没有置顶的则普通推文在 instruction[1]，
但是为了健壮性没有直接取

大体的结构是

instructions(包含置顶的时间线) >> entries(时间线推文) >> result(用户和推文信息) >> legacy(推文信息) >> entities(媒体)

"""


@parse_UserTweet_decorator
def instructions_from_UserTweet_api_obj(obj: dict) -> dict:
    instructions = obj["data"]["user"]["result"]["timeline_v2"]["timeline"][
        "instructions"
    ]
    return instructions


@parse_UserTweet_decorator
# 通过 filter 得到置顶推文
def pin_entry_from_instructions(instructions: list[dict]) -> Optional[dict]:
    return next((i["entry"] for i in instructions if "Pin" in i["type"]), None)


@parse_UserTweet_decorator
# 通过 filter 得到普通推文，因为里面有广告和推荐关注之类的东西，所以要只保留推文和回复
def entries_from_instructions(instructions: list[dict]) -> list:
    entries = next((i["entries"] for i in instructions if "Add" in i["type"]), [])
    return [
        entry
        for entry in entries
        if entry_is_tweet(entry) or entry_is_conversation(entry)
    ]


@parse_UserTweet_decorator
def _result_from_entry(entry: dict) -> dict:
    if entry_is_tweet(entry):
        return entry["content"]["itemContent"]["tweet_results"]["result"]
    elif entry_is_conversation(entry):
        return entry["content"]["items"][-1]["item"]["itemContent"]["tweet_results"][
            "result"
        ]
    else:
        raise Exception("存在不该出现的 entry 类型")


# 从 result 中提取出有用的信息
@parse_UserTweet_decorator
def _info_from_result(result: dict) -> dict:
    ret = {}

    user_legacy = result["core"]["user_results"]["result"]["legacy"]
    legacy = result["legacy"]

    ret["user_id"] = legacy["user_id_str"]
    ret["user_screen_name"] = user_legacy["screen_name"]
    ret["user_name"] = user_legacy["name"]
    ret["user_profile_image"] = user_legacy["profile_image_url_https"]

    ret["id_str"] = legacy["id_str"]
    ret["full_text"] = legacy["full_text"]
    ret["created_time"] = legacy["created_at"]
    ret["created_time_epoch"] = time_str_to_epoch(legacy["created_at"])
    ret["media_url_list"] = _extract_media_from_legacy(legacy)
    ret["retweet_src"] = _extract_retweet_src_from_legacy(legacy)
    ret["quote_src"] = _extract_quote_src_from_legacy(legacy)

    return ret


# 提取媒体信息
@parse_UserTweet_decorator
def _extract_media_from_legacy(legacy: dict) -> list[str]:
    entities = legacy["entities"]
    if "media" not in entities:
        return []

    ret = []
    for media in entities["media"]:
        if media["type"] == "photo":
            ret.append(media["media_url_https"])
        elif media["type"] == "video":
            video_variants = [
                variants
                for variants in media["video_info"]["variants"]
                if "bitrate" in variants
            ]
            best_quality = max(video_variants, key=lambda x: x["bitrate"])["url"]
            ret.append(best_quality)

    return ret


@parse_UserTweet_decorator
def _extract_retweet_src_from_legacy(legacy: dict) -> str | None:
    if "retweeted_status_result" not in legacy:
        return None
    retweeted_legacy = legacy["retweeted_status_result"]["result"]["legacy"]
    retweeted_user_id = retweeted_legacy["user_id_str"]
    retweeted_tweet_id = retweeted_legacy["id_str"]
    return build_twitter_url(retweeted_user_id, retweeted_tweet_id)


@parse_UserTweet_decorator
def _extract_quote_src_from_legacy(legacy: dict) -> str | None:
    if not legacy["is_quote_status"]:
        return None
    return legacy["quoted_status_permalink"]["expanded"]


# 转换时间字符串为时间戳
def time_str_to_epoch(time_str: str):
    # 定义日期时间格式
    date_format = "%a %b %d %H:%M:%S %z %Y"
    # 将字符串转换为 datetime 对象
    dt_object = datetime.strptime(time_str, date_format)
    # 将 datetime 对象转换为 UTC 时间戳
    timestamp_utc = int(dt_object.timestamp())
    return timestamp_utc


"""
对 entry 的一些判断
"""


def id_of_entry(entry):
    return pipe(_result_from_entry, lambda r: r["legacy"]["id_str"])(entry)


def entry_is_tweet(entry: dict) -> bool:
    return "tweet" in entry["entryId"]


def entry_is_conversation(entry: dict) -> bool:
    return "profile-conversation" in entry["entryId"]


"""
@用户名(user_screen_name) 到 用户id(user_id) 的键值对文件操作
"""


class NameIDMap:
    def __init__(self):
        self.NAME_ID_MAP = "name_to_id.json"
        self.NAME_ID_MAP_PATH = os.path.join(os.getcwd(), self.NAME_ID_MAP)
        self._map = self.read_name_id_mapping()

    def read_name_id_mapping(self):
        if not os.path.exists(self.NAME_ID_MAP_PATH):
            return {}
        local = file.read_json_from_file_without_exception(self.NAME_ID_MAP_PATH)
        return local if local is not None else {}

    def save_name_id_mapping(self):
        file.save_as_json(self.NAME_ID_MAP_PATH, self._map)

    def pure_get(self, screen_name: str) -> str:
        if screen_name in self._map:
            return self._map[screen_name]
        return pipe(
            fetch.fetch_id_from_user_screen_name, id_from_UserByScreenName_api_obj
        )(screen_name)

    def get(self, screen_name: str):
        id = self.pure_get(screen_name)
        if screen_name not in self._map:
            self._map[screen_name] = id
        self.save_name_id_mapping()
        return id


name_id_map = NameIDMap()
