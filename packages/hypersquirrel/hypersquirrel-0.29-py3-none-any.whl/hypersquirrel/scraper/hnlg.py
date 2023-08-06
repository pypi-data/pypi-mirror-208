from commmons import html_from_url, get_host_url


def get_thumbnail_path(element):
    div = element.xpath(".//div[contains(@style,'background-image')]")[0]
    return div.attrib["style"].split("url('")[-1].rstrip("');")


def get_title(element):
    spans = element.xpath(".//span")
    if spans:
        return spans[0].text.strip()
    return None


def get_atag(element):
    atags = element.xpath(".//a")
    if atags:
        return atags[0]
    return None


def scrape_hnlg(url):
    host_url = get_host_url(url)
    root = html_from_url(url)

    for post in root.xpath("//a[contains(@href,'/article/')]"):
        href = post.attrib["href"]
        title = get_title(post)
        if not title:
            continue

        post_id = href.split("/")[-1].split("-")[-1].split(".")[0]

        yield {
            "fileid": "hnlg" + post_id,
            "sourceurl": "vpr://" + host_url + href,
            "filename": title,
            "thumbnailurl": host_url + get_thumbnail_path(post)
        }
