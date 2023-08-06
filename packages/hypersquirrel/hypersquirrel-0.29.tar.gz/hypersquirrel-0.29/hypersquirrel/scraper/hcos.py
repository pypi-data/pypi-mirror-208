import itertools

from commmons import head, html_from_url, get_host_url, md5

MAX_TAGS = 3


def _scrape_gallery(gallery, host_url):
    posts = gallery.xpath(".//div[@class='image-list-item']")
    for post in posts:
        atag = head(post.xpath(".//*[@class='image-list-item-title']/a"))
        img = head(post.xpath(".//div[@class='image-list-item-image']//img"))
        if atag is not None and img is not None:
            href = atag.attrib["href"]
            title = atag.text
            if href is not None and title is not None:
                yield {
                    "fileid": "hcos" + md5(href),
                    "filename": title.replace("\n", " "),
                    "sourceurl": "vpr://" + host_url + href,
                    "thumbnailurl": img.attrib["src"]
                }


def _scrape_search_results(root, host_url):
    galleries = root.xpath("//div[@id='display_area_image']")
    for gallery in galleries:
        yield from _scrape_gallery(gallery, host_url)


def _scrape_from_related_tags(root, host_url):
    atags = itertools.islice(root.xpath("//p[@id='detail_tag']//a"), MAX_TAGS)
    for atag in atags:
        href = atag.attrib["href"]
        new_root = html_from_url(host_url + href, headers={
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0"
        })
        yield from _scrape_search_results(new_root, host_url)


def scrape_hcos(url):
    root = html_from_url(url, headers={
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0"
    })
    host_url = get_host_url(url)

    yield from _scrape_search_results(root, host_url)
    yield from _scrape_from_related_tags(root, host_url)
