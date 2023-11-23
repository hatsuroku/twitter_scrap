from tweet_getter import TweetGetter
import json

getter = TweetGetter("yuka_n_RIOT")
# 拉取新推特，但不更新本地
res = getter.get()

# 拉取新推特并且更新本地
res = getter.get_and_update()

with open("out.json", "w", encoding="utf-8") as f:
    json.dump(res.to_json(), f, ensure_ascii=False, indent=4)
