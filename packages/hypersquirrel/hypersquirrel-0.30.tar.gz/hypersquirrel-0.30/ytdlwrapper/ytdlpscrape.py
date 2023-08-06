from typing import Iterator

from commmons import md5
from yt_dlp import YoutubeDL


def scrape_ytdl(url: str) -> Iterator[dict]:
    ydl = YoutubeDL({'outtmpl': '%(id)s.%(ext)s'})

    with ydl:
        result = ydl.extract_info(url, download=False)

    if 'entries' in result:
        # Can be a playlist or a list of videos
        videos = result['entries']
    else:
        # Just a video
        videos = [result]

    for v in videos:
        yield {
            "fileid": md5(v["extractor"]) + v["id"],
            "filename": v["title"],
            "sourceurl": v["original_url"],
            "thumbnailurl": v["thumbnail"]
        }
