from twitter_scrap.tweet_getter import TweetGetter
from twitter_scrap.fetch import fetch
import json
import os

getter = TweetGetter("yuka_n_RIOT")

# 默认 headers json 的路径是 python 运行路径(os.getcwd())下的 headers.json
# 如果需要自行指定 header json 路径，也可以用以下 api
# fetch.update_headers_from_file('./example/ie/example.json')

### 根据自己想要的效果选其中一个 api 调用

# 拉取新推特，但不更新本地
res = getter.get()

# 拉取新推特并且更新本地
# res = getter.get_and_update()

with open("out.json", "w", encoding="utf-8") as f:
    json.dump(res.to_json(), f, ensure_ascii=False, indent=4)