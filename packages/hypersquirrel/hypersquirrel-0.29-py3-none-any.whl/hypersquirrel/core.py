import itertools
import sys
from dataclasses import dataclass, field
from typing import Iterator, Callable


@dataclass
class Watchlist:
    url: str
    max_items: int = field(default=None)
    page_min: int = field(default=1)
    page_max: int = field(default=1)

    @property
    def is_multipage(self):
        return "${page}" in self.url

    def __post_init__(self):
        assert self.url
        if self.is_multipage:
            assert isinstance(self.page_min, int)
            assert isinstance(self.page_max, int)
            assert self.page_min < self.page_max

    def scrape(self, scraper: Callable[[str], Iterator[dict]], url=None):
        def generate():
            for page in range(self.page_min, self.page_max + 1):
                substituted_url = (url or self.url).replace("${page}", str(page))
                yield from scraper(substituted_url)

        yield from itertools.islice(generate(), self.max_items or sys.maxsize)
