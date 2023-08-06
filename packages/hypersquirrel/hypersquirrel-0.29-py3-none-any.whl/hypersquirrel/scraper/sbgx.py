from commmons import html_from_url


def get_title_and_url(div):
    h2s = div.xpath(".//h2[contains(@class, 'post-title')]")
    if h2s:
        a = h2s[0].xpath("./a")[0]
        return a.text, a.attrib["href"]
    return None


def get_thumbnail_url(div):
    return div.xpath(".//meta[@itemprop='image']")[0].attrib["content"]


def scrape_sbgx(url):
    root = html_from_url(url)

    for div in root.xpath("//div[@class='post-outer']"):
        title_and_url = get_title_and_url(div)
        if not title_and_url:
            continue

        fileid = "sbgx" + div.xpath('.//a[@name]')[0].attrib["name"]
        title, url = title_and_url

        yield {
            "fileid": fileid,
            "filename": title,
            "sourceurl": "vpr://" + url,
            "thumbnailurl": get_thumbnail_url(div)
        }
