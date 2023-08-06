from typing import Iterator


def interpret(url: str) -> Iterator[dict]:
    post_id = [x for x in url.split("/") if x][-1]
    yield {
        "fileid": post_id,
        "filename": f"Instagram {post_id}",
        "sourceurl": url,
        "tags": [
            "instagram"
        ]
    }
