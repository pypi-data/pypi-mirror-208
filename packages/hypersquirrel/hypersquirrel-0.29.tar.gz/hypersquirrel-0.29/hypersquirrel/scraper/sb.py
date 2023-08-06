from commmons import get_host_url
from lxml import html


def scrape(url):
    def get_body_with_ytdl() -> str:
        from yt_dlp import YoutubeDL
        ytdl = YoutubeDL()
        ie = ytdl.get_info_extractor("SpankBang")
        mobj = ie._match_valid_url(url)
        video_id = mobj.group('id') or mobj.group('id_2')
        return ie._download_webpage(
            url.replace('/%s/embed' % video_id, '/%s/video' % video_id),
            video_id, headers={'Cookie': 'country=US'})

    tree = html.fromstring(get_body_with_ytdl())
    host_url = get_host_url(url)

    divs = tree.xpath("//div[contains(@class, 'video-item')]")
    for div in divs:
        if "data-id" not in div.attrib:
            continue

        dataid = div.attrib["data-id"]
        atags = div.xpath("./a")

        if not atags:
            continue

        imgs = div.xpath("./a/picture/img")
        if not imgs:
            continue

        atag = atags[0]
        img = imgs[0]

        yield {
            "fileid": "sb" + dataid,
            "sourceurl": host_url + atag.attrib["href"],
            "filename": img.attrib["alt"],
            "thumbnailurl": img.attrib["data-src"]
        }
