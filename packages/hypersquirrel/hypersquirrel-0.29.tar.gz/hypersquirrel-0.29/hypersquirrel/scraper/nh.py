from typing import Optional

from bs4 import Tag, BeautifulSoup, PageElement
from commmons import get_host_url

from hypersquirrel.util import soup_from_url

MEDIABOOK_ENABLED = False


def get_vkey_href_title(li: Tag):
    vkey: str = li.attrs.get("data-video-vkey")
    href = f"view_video.php?viewkey={vkey}"
    title = None
    a = li.find("a", attrs=dict(href=f"/{href}"))
    if a:
        title = a.attrs.get("title")
    return vkey, href, title


def get_profile_name(soup: BeautifulSoup) -> Optional[str]:
    div = soup.find("div", class_="nameSubscribe")
    if div:
        return div.find("h1").text.strip()


def try_append_thumbnail(li: PageElement, file: dict, attrs: dict):
    img = li.find("img", class_="thumb", attrs=attrs)

    if not img:
        return

    thumbnailurl = img.attrs.get("src")
    if thumbnailurl:
        file["thumbnailurl"] = thumbnailurl

    if MEDIABOOK_ENABLED:
        mediabook = img.attrs.get("data-mediabook")
        if mediabook:
            file["thumbnailvideourl"] = mediabook


def scrape(url):
    soup = soup_from_url(url)
    profile_name = get_profile_name(soup)

    for li in soup.find_all("li", class_="videoblock"):
        def try_append_uploader(title: str) -> str:
            uploader = profile_name
            if not uploader:
                usrdiv = li.find("div", class_="usernameWrap")
                if usrdiv:
                    uploader = usrdiv.find("a").text

            return f"[{uploader}] {title}" if uploader else title

        vkey, href, title = get_vkey_href_title(li)
        if title:
            file = dict(
                fileid=vkey,
                sourceurl=f"{get_host_url(url)}/{href}",
                filename=try_append_uploader(title.strip())
            )

            try_append_thumbnail(li, file, attrs={"alt": title})

            yield file
