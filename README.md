# twitter_scrap

用来拉取某人新推特的工具

## 注意事项

本地缓存文件夹默认为 `cache` 文件夹，screen_name 到 user_id 的缓存为 `name_to_id.json`，请不要随意删除这些文件。

## 使用方法

首先修改 `header.json` 里的内容，其中空字段可以在随便访问一个推特用户的首页时用浏览器后台的 Network 功能，搜索 `UserTweet` 获得你自己的内容，并且填充进 `header.json` 中。

![](assets/2023-11-23-16-40-06-image.png)

用法可以在 `demo.py` 中查看，主要使用 `TwiterGetter` 的两个方法：

```python
from tweet_getter import TweetGetter
import json

getter = TweetGetter("yuka_n_RIOT")
# 拉取新推特，但不更新本地
res = getter.get()

# 拉取新推特并且更新本地
res = getter.get_and_update()

with open("out.json", "w", encoding="utf-8") as f:
    json.dump(res.to_json(), f, ensure_ascii=False, indent=4)
```

## 工程结构

```bash
│  cache_io.py            # 本地缓存的读写
│  decoder.py             # 核心文件，用于从 twitter API 返回的 json 提取关键字段
│  demo.py                # 使用范例
│  fetch.py               # 网络请求相关
│  file.py                # 文件底层操作
│  functional.py          # 函数式编程辅助库
│  LICENSE
│  name_to_id.json        # screen_name 到 user_id 的本地缓存，如不存在则会在初次使用时生成
│  tweet.py               # 提取出的关键字段
│  tweet_getter.py        # 对外暴露的 api
│  updater.py             # 更新策略相关
│
├─cache                   # 用户推特缓存，如不存在则会在初次使用时生成
│      user_name---1122334455667788.json
│
```
