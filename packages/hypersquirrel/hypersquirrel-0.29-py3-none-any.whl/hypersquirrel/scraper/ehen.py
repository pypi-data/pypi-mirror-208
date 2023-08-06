from commmons import head

from hypersquirrel.util import html_from_url_with_headers


def _to_post_id(post_url: str) -> str:
    return post_url.split("/g/")[-1].split("/")[0]


def _get_file(post):
    atag = head(post.xpath(".//td[contains(@class, 'glname')]/a"))
    if atag is not None:
        post_url = atag.attrib["href"]
        post_id = _to_post_id(post_url)
        if post_id.isnumeric():
            img = head(post.xpath(f"//div[@class='glthumb' and @id='it{post_id}']//img"))
            if img is not None:
                data_source = img.attrib.get("data-src")
                source = img.attrib.get("src")
                yield {
                    "fileid": "ehen" + post_id,
                    "filename": img.attrib["title"],
                    "sourceurl": "vpr://" + post_url,
                    "thumbnailurl": data_source or source
                }


def _get_posts(root):
    posts = root.xpath("//table[contains(@class, 'itg') and contains(@class, 'gltc')]//tr")
    for post in posts:
        yield from _get_file(post)


def _get_uploader_url(root) -> str:
    atag = head(root.xpath("//div[@class='gm']//div[@id='gdn']/a[contains(@href, '/uploader/')]"))
    if atag is not None:
        return atag.attrib["href"]
    return None


def scrape_ehen(url):
    root = html_from_url_with_headers(url)
    yield from _get_posts(root)

    uploader_url = _get_uploader_url(root)
    if uploader_url is not None:
        root = html_from_url_with_headers(uploader_url)
        yield from _get_posts(root)
