from commmons import md5
from htmllistparse import htmllistparse, FileEntry


def to_file(url, entry: FileEntry) -> dict:
    full_url = f"{url}/{entry.name}"
    fileid = md5(full_url)
    return {
        "fileid": fileid,
        "sourceurl": full_url,
        "filename": entry.name.strip()
    }


def scrape(url):
    clean_url = url.rstrip("/")
    cwd, listing = htmllistparse.fetch_listing(clean_url)
    return [to_file(clean_url, x) for x in listing]
