from typing import Callable, Iterator

from .core import Watchlist
from .scraper import youtubeapi
from .scraper.buondua import scrape_buondua
from .scraper.cosplayporntube import scrape_cpt
from .scraper.drts import scrape_drts
from .scraper.ehen import scrape_ehen
from .scraper.fseg import scrape as scrape_fseg_html
from .scraper.googleimagesearch import scrape_gimg
from .scraper.hcos import scrape_hcos
from .scraper.hnlg import scrape_hnlg
from .scraper.lgbb import scrape_lgbb
from .scraper.nh import scrape as scrape_nh_html
from .scraper.nlgs import scrape_uulg, scrape_nlgs, scrape_lgcx
from .scraper.opendir import scrape as scrape_opendir
from .scraper.reddit import scrape_reddit_rss, scrape_reddit_json
from .scraper.sb import scrape as scrape_sb_html
from .scraper.sbgx import scrape_sbgx
from .scraper.v2ph import scrape_v2ph
from .scraper.vg import scrape_vipergirls as scrape_vg_html
from .scraper.xh import scrape as scrape_xh_html
from .scraper.xv import scrape as scrape_xv_html
from .scraper.hellp import scrape as scrape_hellp


class WatchlistScraperFactory:
    def __init__(self):
        self.registry = list()

    def register_scraper(self, predicate: Callable[[Watchlist], bool],
                         scraper: Callable[[str], Iterator[dict]]):
        self.registry.append((predicate, scraper,))

    def get_scraper(self, watchlist: Watchlist):
        for registry_pair in self.registry:
            condition = registry_pair[0]
            scraper = registry_pair[1]
            if condition(watchlist):
                return scraper
        # Default: opendir
        return scrape_opendir


_wsf = WatchlistScraperFactory()

get_scraper = _wsf.get_scraper
register_scraper = _wsf.register_scraper

register_scraper(lambda w: "pornhub.com" in w.url, scrape_nh_html)
register_scraper(lambda w: "vipergirls" in w.url, scrape_vg_html)
register_scraper(lambda w: "xhamster" in w.url, scrape_xh_html)
register_scraper(lambda w: "xvideos.com" in w.url, scrape_xv_html)
register_scraper(lambda w: "spankbang.com" in w.url, scrape_sb_html)
register_scraper(lambda w: "reddit" in w.url and "json?feed" in w.url, scrape_reddit_json)
register_scraper(lambda w: "reddit" in w.url, scrape_reddit_rss)
register_scraper(lambda w: "v2ph" in w.url, scrape_v2ph)
register_scraper(lambda w: "hentai-cosplays" in w.url, scrape_hcos)
register_scraper(lambda w: "buondua" in w.url, scrape_buondua)
register_scraper(lambda w: "e-hentai" in w.url, scrape_ehen)
register_scraper(lambda w: "cosplayporntube" in w.url, scrape_cpt)
register_scraper(lambda w: "egirls" in w.url, scrape_fseg_html)
register_scraper(lambda w: "nlegs" in w.url, scrape_nlgs)
register_scraper(lambda w: "uuleg" in w.url, scrape_uulg)
register_scraper(lambda w: "honeyleg" in w.url, scrape_hnlg)
register_scraper(lambda w: "legbabe" in w.url, scrape_lgbb)
register_scraper(lambda w: "leg.cx" in w.url, scrape_lgcx)
register_scraper(lambda w: "superbeautygirlx" in w.url, scrape_sbgx)
register_scraper(lambda w: "porn-images-xxx" in w.url, scrape_hcos)
register_scraper(lambda w: "hentai-img" in w.url, scrape_hcos)
register_scraper(lambda w: "google" in w.url, scrape_gimg)
register_scraper(lambda w: "dirtyship" in w.url, scrape_drts)
register_scraper(lambda w: "hellporno" in w.url, scrape_hellp)
register_scraper(lambda w: "youtube" in w.url, youtubeapi.scrape_youtubeapi)
