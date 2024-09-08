from datetime import datetime

import feedparser
import requests

rss_url = "https://rsshub.app/meituan/tech"

# 抓取RSS源内容
response = requests.get(rss_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
response.raise_for_status()  # 如果状态码不是200，抛出HTTPError

feed = feedparser.parse(response.text)

print(feed)

# print(feed.bozo)

# print(feed.feed)

# print(feed.entries)

# for entry in feed.entries:
#     print(entry)
#     print(entry.title)
#     print(entry.link)
#     print(entry.published)
#     # print(entry.published)
