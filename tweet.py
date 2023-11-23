from typing import Optional, List
import json


def build_twitter_url(user_id_or_screen_name: str, tweet_id):
    return f"https://twitter.com/{user_id_or_screen_name}/status/{tweet_id}"


class Timeline:
    def __init__(self, pin=None, tweets=None):
        self.pin: Optional[Tweet] = pin
        self.tweets: List[Tweet] = [] if tweets is None else tweets

    def __repr__(self):
        # 获取对象的所有属性
        # 使用json.dumps将字典转成JSON格式的字符串
        return json.dumps(self.to_json(), indent=2, ensure_ascii=False)

    def to_json(self):
        return {
            "pin": None if self.pin is None else self.pin.to_json(),
            "tweets": [tweet.to_json() for tweet in self.tweets],
        }


class Tweet:
    def __init__(
        self,
        *,
        id_str="",
        user_id="",
        user_screen_name="",
        user_name="",
        user_profile_image="",
        full_text="",
        created_time="",
        created_time_epoch=0,
        media_url_list=None,
        retweet_src=None,
        quote_src=None,
    ):
        self.id_str = id_str
        self.user_id = user_id
        self.user_screen_name = user_screen_name
        self.user_name = user_name
        self.user_profile_image = user_profile_image
        self.url = build_twitter_url(self.user_screen_name, id_str)
        self.full_text = full_text
        self.created_time = created_time
        self.created_time_epoch = created_time_epoch
        self.media_url_list = [] if media_url_list is None else media_url_list
        self.retweet_src = retweet_src
        self.quote_src = quote_src

    def to_json(self):
        return self.__dict__.copy()

    def __repr__(self):
        # 使用json.dumps将字典转成JSON格式的字符串
        return json.dumps(self.__dict__, indent=2, ensure_ascii=False)
