import os
from dataclasses import dataclass
from typing import Union

import requests
from commmons import head, get_query_params

CHANNELS_API_URL = "https://www.googleapis.com/youtube/v3/channels"
VIDEOS_API_URL = "https://www.googleapis.com/youtube/v3/videos"


@dataclass
class UploadIdFinder:
    USE_API_TO_FIND_UPLOAD_ID = False

    url: str
    apikey: str

    def _get_url_component(self, preceding_component: str) -> Union[str, None]:
        if f"{preceding_component}/" in self.url:
            return head(self.url.split(f"{preceding_component}/")[1].split("/"))
        return None

    def _to_upload_id(self, external_id: str):
        if UploadIdFinder.USE_API_TO_FIND_UPLOAD_ID:
            body = requests.get(CHANNELS_API_URL, params={
                "part": "contentDetails",
                "id": external_id,
                "key": self.apikey
            }).json()

            return body["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

        return "UU" + external_id.lstrip("UC")

    def _get_upload_id_by_watch(self) -> str:
        video_id = get_query_params(self.url).get("v") or self._get_url_component("watch")
        body = requests.get(VIDEOS_API_URL, params=dict(
            id=video_id,
            part='id,snippet',
            type='channel',
            key=self.apikey
        )).json()
        channel_id = head(body["items"])["snippet"]["channelId"]
        return self._to_upload_id(channel_id)

    def _get_upload_id_by_channel(self) -> str:
        channel_id = self._get_url_component('channel')
        return self._to_upload_id(channel_id)

    def _get_upload_id_by_user(self) -> str:
        username = self._get_url_component('user')
        body = requests.get(CHANNELS_API_URL, params={
            "part": "id",
            "forUsername": username,
            "key": self.apikey
        }).json()
        external_id = head(body.get("items", [{}]))["id"]
        return self._to_upload_id(external_id)

    def get_upload_id(self) -> str:
        upload_id_map = dict(
            channel=self._get_upload_id_by_channel,
            user=self._get_upload_id_by_user,
            watch=self._get_upload_id_by_watch
        )

        existing_key = head([key for key in upload_id_map.keys() if f"/{key}" in self.url])
        func = upload_id_map[existing_key]
        return func()


def get_playlist_id(url: str) -> Union[str, None]:
    if "/playlist?list=" in url:
        return get_query_params(url).get("list")

    return None


def get_adequate_thumbnail_url(thumbnails: dict) -> Union[str, None]:
    if not thumbnails:
        return None

    if "medium" in thumbnails:
        return thumbnails["medium"]["url"]

    return thumbnails.get(head(list(thumbnails.keys())))


def get_all_videos(upload_id: str, apikey: str):
    url = "https://www.googleapis.com/youtube/v3/playlistItems"
    params = {
        "playlistId": upload_id,
        "key": apikey,
        "part": "snippet",
        "maxResults": 50
    }

    while True:
        body = requests.get(url, params=params).json()

        for item in body["items"]:
            snippet = item["snippet"]
            video_id = snippet["resourceId"]["videoId"]
            thumbnailurl = get_adequate_thumbnail_url(snippet["thumbnails"])
            yield {
                "fileid": video_id,
                "filename": snippet["title"],
                "sourceurl": f"https://youtube.com/watch/{video_id}",
                "thumbnailurl": thumbnailurl
            }

        next_page_token = body.get("nextPageToken")

        if not next_page_token:
            break

        params["pageToken"] = next_page_token


def scrape_youtubeapi(url: str):
    apikey = os.getenv("YOUTUBE_APIKEY")
    playlist_id = get_playlist_id(url)

    if not playlist_id:
        print("Getting upload_id as a substitute")
        playlist_id = UploadIdFinder(url, apikey).get_upload_id()

    yield from get_all_videos(playlist_id, apikey)
