import json

from commmons import get_host_url, html_from_url


def get_file_divs(root):
    divs = root.xpath("//div[@data-id]")
    for div in divs:
        if "data-id" in div.attrib:
            yield div


def get_file_from_div(div, host_url):
    fileid = div.attrib["data-id"]
    atag = div.xpath(f".//a[@title and contains(@href, '{fileid}')]")[0]
    file = {
        "fileid": "xv" + fileid,
        "sourceurl": host_url + atag.attrib["href"],
        "filename": atag.attrib["title"]
    }

    imgs = div.xpath("./div/div/a/img")
    if imgs:
        file["thumbnailurl"] = imgs[0].attrib["data-src"]

    return file


def get_related_files(host_url, root):
    for script_tag in root.xpath("//script"):
        if script_tag.text:
            text = script_tag.text.strip()
            if not text.startswith("var video_related"):
                continue
            json_str = '='.join(script_tag.text.split('=')[1:]).split('];')[0] + "]"
            items = json.loads(json_str)
            for item in items:
                yield {
                    "fileid": f"xv{item['id']}",
                    "filename": str(item["tf"]),
                    "sourceurl": host_url + str(item["u"]),
                    "thumbnailurl": str(item["i"])
                }


def scrape(url):
    host_url = get_host_url(url)
    root = html_from_url(url)
    for div in get_file_divs(root):
        file = get_file_from_div(div, host_url)
        yield file

    yield from get_related_files(host_url, root)
