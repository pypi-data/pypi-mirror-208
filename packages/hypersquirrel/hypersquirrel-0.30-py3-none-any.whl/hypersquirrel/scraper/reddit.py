import json
import time
from random import random
from types import SimpleNamespace

import feedparser
import requests
from commmons import head, breakdown
from pydash import get

REDDIT_API_COOLDOWN_DURATION = 2  # seconds
REDDIT_JSON_MAX_PAGES = 3


def cooldown():
    offset = random()  # introduce a bit of randomness by varying the cooldown duration.
    time.sleep(REDDIT_API_COOLDOWN_DURATION + offset)


def scrape_reddit_rss(rss_url: str):
    def should_skip(entry):
        content = head(entry["content"])
        return content is None or "gif" not in content["value"]

    def get_thumbnailurl(entry: dict):
        url_dict = head(entry.get("media_thumbnail"))
        if url_dict is not None:
            return url_dict.get("url")
        return None

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


def scrape_reddit_json(json_url: str):
    url, query_params = breakdown(json_url)
    next_token = SimpleNamespace(value="")

    def scrape_with_next_token():
        if next_token.value:
            query_params["after"] = [next_token.value]

        r = requests.get(url, headers={"User-Agent": "debian:hypersquirrel:0.1"}, params=query_params)
        rjson = json.loads(r.text)
        next_token.value = get(rjson, "data.after")

        posts = get(rjson, "data.children", list())
        for post in posts:
            data = post["data"]
            media_type = get(data, "secure_media.oembed.type")
            url_overridden_by_dest = get(data, "url_overridden_by_dest")
            permalink = get(data, "permalink")
            if media_type == "video" or "gif" in url_overridden_by_dest:
                yield {
                    "fileid": data["name"],
                    "sourceurl": url_overridden_by_dest or permalink,
                    "filename": data["title"],
                    "thumbnailurl": data["thumbnail"],
                }

    for i in range(REDDIT_JSON_MAX_PAGES):
        yield from scrape_with_next_token()
        if not next_token.value:
            break
        cooldown()
