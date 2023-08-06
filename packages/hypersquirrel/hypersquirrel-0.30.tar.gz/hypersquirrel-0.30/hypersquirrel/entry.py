import re
from typing import Iterator, List

from hypersquirrel.core import Watchlist
from hypersquirrel.literalinterpreterfactory import get_interpreter
from hypersquirrel.scraperfactory import get_scraper

PAGED_PATTERN = re.compile("<\d+-\d+>")


def create_watchlist(url: str, max_items: int):
    match = PAGED_PATTERN.findall(url)
    if len(match) == 1:
        pages = match[0].replace("<", "").replace(">", "").split("-")
        return Watchlist(
            url=url.replace(match[0], "${page}"),
            max_items=max_items,
            page_min=int(pages[0]),
            page_max=int(pages[1])
        )
    return Watchlist(
        url=url,
        max_items=max_items
    )


def scrape(w: Watchlist) -> Iterator[dict]:
    return w.scrape(get_scraper(w))


def scrape_literal_urls(urls: List[str]) -> dict:
    for url in set(urls):
        interpreter = get_interpreter(url)
        if interpreter:
            yield from interpreter(url)
