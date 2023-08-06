import requests
from commmons import html_from_url, merge
from bs4 import BeautifulSoup

_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0",
    "Cache-Control": "no-cache, no-store, must-revalidate",
    "Pragma": "no-cache",
    "Expires": "0"
}


def html_from_url_with_headers(url, referer=None):
    headers = merge(_HEADERS, dict(Referer=referer or url))
    return html_from_url(url, headers=headers)


def soup_from_url(url, **kwargs):
    s = requests.Session()
    r = s.get(url, headers=_HEADERS, **kwargs)
    return BeautifulSoup(r.text, "lxml")
