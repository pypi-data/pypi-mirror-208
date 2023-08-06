from typing import Iterator

from commmons import head, md5
from lxml.html import HtmlElement

from hypersquirrel.util import html_from_url_with_headers


def find_files(root: HtmlElement, li_class: str):
    for li in root.xpath(f"//li[@class='{li_class}']"):
        a = head(li.xpath(".//a"))
        img = head(li.xpath(".//img"))
        if img is None or a is None:
            continue

        thumbnail_url = img.attrib["src"]
        title = img.attrib["alt"]
        href = a.attrib["href"]

        yield {
            "fileid": f"drts{md5(href)}",
            "sourceurl": href,
            "filename": title,
            "thumbnailurl": thumbnail_url
        }


def vids(root: HtmlElement):
    yield from find_files(root, "thumi")


def pics(root: HtmlElement):
    for file in find_files(root, "thumbphoto"):
        source_url = file["sourceurl"]
        if "gallery" in source_url:
            yield {
                **file,
                "sourceurl": f"vpr://{source_url}"
            }


def scrape_drts(url: str) -> Iterator[dict]:
    root = html_from_url_with_headers(url)
    yield from vids(root)
    yield from pics(root)
