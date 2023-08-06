from commmons import get_host_url

from hypersquirrel.util import soup_from_url


def sanitize(text):
    text = text.replace("\n", " ")
    while "  " in text:
        text = text.replace("  ", " ")

    return text


def scrape_v2ph(url):
    soup = soup_from_url(url)

    for div in soup.find_all("div", class_="thumbnail card"):
        a = div.find("a", class_="media-cover")
        img = div.find("img")
        if img is None:
            continue

        file = {
            "fileid": "v2ph" + a.attrs["href"].split("/")[-1].split(".")[0].split("?")[0],
            "filename": img.attrs["alt"],
            "sourceurl": "vpr://" + get_host_url(url) + a.attrs["href"],
            "thumbnailurl": img.attrs["data-src"]
        }

        media_meta = div.find_next("div", class_="media-meta")
        if media_meta:
            file["filename"] = sanitize(media_meta.text)

        yield file
