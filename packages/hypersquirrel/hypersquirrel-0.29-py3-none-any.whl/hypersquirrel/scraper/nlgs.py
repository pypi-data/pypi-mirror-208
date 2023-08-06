from commmons import html_from_url, get_host_url


def _get_thumbnail_path(element):
    div = element.xpath(".//div[contains(@style,'background-image')]")[0]
    return div.attrib["style"].split("url('")[-1].rstrip("');")


def _get_title(element):
    spans = element.xpath(".//span")
    if spans:
        return spans[0].text.strip()
    return None


def _s(url, prefix):
    host_url = get_host_url(url)
    root = html_from_url(url)

    for post in root.xpath("//div[contains(@class, 'col-md')]"):
        title = _get_title(post)
        if not title:
            continue

        href = post.xpath(".//a")[0].attrib["href"]
        post_id = href.split("/")[-1].split("-")[-1].split(".")[0]

        yield {
            "fileid": prefix + post_id,
            "sourceurl": "vpr://" + host_url + href,
            "filename": title,
            "thumbnailurl": host_url + _get_thumbnail_path(post)
        }


def scrape_nlgs(url):
    yield from _s(url, "nlgs")


def scrape_uulg(url):
    yield from _s(url, "uulg")


def scrape_lgcx(url):
    yield from _s(url, "lgcx")
