from typing import Iterator

from commmons import html_from_url, head, md5, last

PREFIX = md5("HellPorno")


def scrape_div(div):
    atag = head(div.xpath(".//a"))
    if atag is None:
        return

    imgtag = head(div.xpath(".//img"))
    if imgtag is None:
        return

    span = head(div.xpath(".//*[@class='video-title']"))
    if span is None:
        return

    sourceurl: str = atag.attrib["href"]
    fileid = PREFIX + last([s for s in sourceurl.split("/") if s])

    yield dict(
        fileid=fileid,
        filename=span.text,
        sourceurl=sourceurl,
        thumbnailurl=imgtag.attrib["src"]
    )


def scrape(url: str) -> Iterator[dict]:
    root = html_from_url(url, headers={
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0"
    })

    divs = root.xpath("//div[@class='thumb']")

    for div in divs:
        yield from scrape_div(div)
