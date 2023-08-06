from commmons import html_from_url, get_host_url, strip_tags, html_to_string


def get_post_id(post) -> str:
    return post.attrib["data-content"].strip("post-")


def get_post_url(url, postid) -> str:
    if "page" in url:
        urlsplit = url.split("/")
        url = "".join(urlsplit[:len(urlsplit) - 2])

    return url.strip("/") + f"/post-{postid}"


def get_thumbnail_url(post, host_url):
    imgs = post.xpath(".//img")
    if not imgs:
        return None

    img_attrib = imgs[len(imgs) // 2].attrib
    for key in ("data-url", "src"):
        if key in img_attrib:
            val = img_attrib[key]
            if val.startswith("/"):
                return host_url + val
            return val

    return None


def scrape(url):
    root = html_from_url(url)
    posts = root.xpath("//article[contains(@data-content, 'post-')]")

    title_div = root.xpath("//div[contains(@class, 'p-title')]")[0]
    title = strip_tags(html_to_string(title_div))

    host_url = get_host_url(url)

    for p in posts:
        postid = get_post_id(p)
        yield {
            "fileid": f"fseg{postid}",
            "filename": f"{postid}-{title}",
            "sourceurl": get_post_url(url, postid),
            "thumbnailurl": get_thumbnail_url(p, host_url)
        }
