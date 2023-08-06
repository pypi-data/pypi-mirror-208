from commmons import html_from_url, get_host_url


def get_title(element):
    h3s = element.xpath("//h3")
    if h3s:
        return h3s[0].text.strip("\n").strip()

    return None


def get_thumbnail_path(element):
    imgs = element.xpath(".//div[@class='divimg']/img")
    if imgs:
        return imgs[0].attrib["src"]
    return None


def scrape_lgbb(url):
    host_url = get_host_url(url)
    root = html_from_url(url)

    for div in root.xpath("//div[@class='panel panel-default']"):
        title = get_title(div)
        if not title:
            continue

        thumbnail_path = get_thumbnail_path(div)
        if not thumbnail_path:
            continue

        href = div.xpath('.//a')[0].attrib["href"]
        post_id = href.split("/")[-1].split("-")[-1].split(".")[0]

        yield {
            "fileid": "lgbb" + post_id,
            "sourceurl": "vpr://" + host_url + href,
            "filename": title,
            "thumbnailurl": host_url + thumbnail_path
        }
