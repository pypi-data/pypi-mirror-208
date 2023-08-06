import time
from random import random

import feedparser
import requests
from commmons import head

REDDIT_API_COOLDOWN_DURATION = 2  # seconds


def cooldown():
    offset = random()  # introduce a bit of randomness by varying the cooldown duration.
    time.sleep(REDDIT_API_COOLDOWN_DURATION + offset)


def should_skip(entry):
    content = head(entry["content"])
    return content is None or "gif" not in content["value"]


def get_thumbnailurl(entry: dict):
    url_dict = head(entry.get("media_thumbnail"))
    if url_dict is not None:
        return url_dict.get("url")
    return None


def scrape_subreddit(rss_url: str):
    assert ".rss" in rss_url
    r = requests.get(rss_url, headers={"User-Agent": "debian:hypersquirrel:0.1"})
    root = feedparser.parse(r.text)

    for entry in root["entries"]:
        if should_skip(entry):
            continue

        yield {
            "fileid": entry["id"],
            "sourceurl": entry["link"],
            "filename": entry["title"],
            "thumbnailurl": get_thumbnailurl(entry)
        }

    # Reduce the risk of getting banned
    cooldown()
