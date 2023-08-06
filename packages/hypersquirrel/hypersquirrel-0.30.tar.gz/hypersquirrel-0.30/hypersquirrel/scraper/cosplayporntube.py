from commmons import md5, head

from hypersquirrel.util import html_from_url_with_headers


def _get_thumb_url(item) -> str:
    try:
        thumbdiv = head(item.xpath(".//div[@class='thumb']"))
        return thumbdiv.attrib["style"].split("(")[-1].rstrip(");")
    except:
        pass
    return None


def scrape_cpt(url: str):
    root = html_from_url_with_headers(url)
    for item in root.xpath("//div[@class='item']"):
        atag = head(item.xpath(".//a"))
        if atag is not None:
            abs_link = atag.attrib["href"]
            if abs_link.startswith("https://cosplayporntube.com/tag"):
                continue
            yield {
                "fileid": "cpt" + md5(abs_link),
                "filename": atag.attrib["title"],
                "sourceurl": abs_link,
                "thumbnailurl": _get_thumb_url(item)
            }
