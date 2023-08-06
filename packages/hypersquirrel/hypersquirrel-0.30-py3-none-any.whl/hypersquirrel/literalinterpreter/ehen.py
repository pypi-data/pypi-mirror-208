from typing import Iterator

from hypersquirrel.scraper.ehen import _to_post_id


def interpret(url: str) -> Iterator[dict]:
    post_id = _to_post_id(url)
    yield {
        "fileid": f"ehen{post_id}",
        "filename": f"ehentai {post_id}",
        "sourceurl": "vpr://" + url,
        "tags": [
            "ehentai"
        ]
    }
