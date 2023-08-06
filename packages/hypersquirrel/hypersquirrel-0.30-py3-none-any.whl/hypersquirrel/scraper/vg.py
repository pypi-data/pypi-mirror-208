from random import sample

from commmons import get_host_url, strip_query_params, html_from_url, head, strip_non_numeric
from vripper.forum.threadfactory import get_thread


def sanitize_title(title, thread_id, reply_index) -> str:
    suffix = f" Reply {reply_index}" if reply_index > 0 else ""
    return title.lstrip(thread_id).replace("-", " ").strip() + suffix


def _get_reply_count(row):
    li = head(row.xpath(".//ul[contains(@class, 'threadstats')]/li"))
    if li is not None:
        atag = head(li.xpath("./a"))
        if atag is not None:
            return int(strip_non_numeric(atag.text))
    return 0


def _get_reply_indices(replies, last=3, rand=2):
    fullrange = range(0, replies + 1)
    if replies <= (last + rand):
        return fullrange

    s = sample(fullrange[:-last], rand)
    s.extend(range(replies, replies - last, -1))
    return s


def _scrape_search_results(url, tree):
    rows = tree.xpath("//div[contains(@class, 'nonsticky')]")
    for row in rows:
        title_node = head(row.xpath(".//*[@class='threadtitle']/a[contains(@class, 'title')]"))
        if title_node is not None:
            href = title_node.attrib["href"].split("?s=")[0]
            if not href.startswith('threads/'):
                continue

            thread_title = href.lstrip("threads/")
            thread_id = thread_title.split('-')[0]
            replies = _get_reply_count(row)

            for i in _get_reply_indices(replies):
                yield {
                    'fileid': thread_id + (f"r{i}" if i > 0 else ""),
                    'filename': sanitize_title(thread_title, thread_id, i),
                    'sourceurl': f"vpr://{get_host_url(url)}/{href}" + (f"?r={i}" if i > 0 else "")
                }


def _scrape_in_thread(thread_url):
    t = get_thread(thread_url)
    for reply_index, p in enumerate(t.posts):
        if len(p.images) == 0:
            continue
        f = {
            "fileid": t.id + (f"r{reply_index}" if reply_index > 0 else ""),
            "filename": t.title + (f" Reply {reply_index}" if reply_index > 0 else ""),
            "sourceurl": f"vpr://{p.url}"
        }
        img = head(p.images)
        if img:
            f.update({"thumbnailurl": img.thumb_url})
        yield f


def scrape_vipergirls(url):
    if "/threads/" in url:
        yield from _scrape_in_thread(strip_query_params(url))
    else:
        tree = html_from_url(url)
        yield from _scrape_search_results(url, tree)
