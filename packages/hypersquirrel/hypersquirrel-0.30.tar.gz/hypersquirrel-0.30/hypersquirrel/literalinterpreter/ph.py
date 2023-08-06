from typing import Iterator

from commmons import get_query_params
from pydash import head


def interpret(url: str) -> Iterator[dict]:
    query_params = get_query_params(url)
    viewkey: str = head(query_params.get("viewkey"))
    if viewkey:
        assert viewkey.startswith("ph")
        yield {
            "fileid": viewkey,
            "filename": viewkey,
            "sourceurl": f"https://www.pornhub.com/view_video.php?viewkey={viewkey}",
            "tags": ["ph"]
        }
