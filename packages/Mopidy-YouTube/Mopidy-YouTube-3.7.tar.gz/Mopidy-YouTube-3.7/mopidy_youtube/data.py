import json
import re
from urllib.parse import parse_qs, urlparse

from mopidy_youtube.apis.ytm_item_to_video import ytm_item_to_video

uri_video_regex = re.compile("^(?:youtube|yt):video:(?P<videoid>.{11})$")
uri_playlist_regex = re.compile("^(?:youtube|yt):playlist:(?P<playlistid>.+)$")
uri_channel_regex = re.compile("^(?:youtube|yt):channel:(?P<channelid>.+)$")
uri_preload_regex = re.compile(
    "^(?:youtube|yt):video:(?P<videoid>.{11}):preload:(?P<preload_data>.+)$"
)


old_uri_video_regex = re.compile(r"^(?:youtube|yt):video/(?:.+)\.(?P<videoid>.+)$")
old_uri_playlist_regex = re.compile(
    r"^(?:youtube|yt):playlist/(?:.+)\.(?P<playlistid>.+)$"
)
old_uri_channel_regex = re.compile(
    r"^(?:youtube|yt):channel/(?:.+)\.(?P<channelid>.+)$"
)


def format_video_uri(id) -> str:
    return f"youtube:video:{id}"


def format_playlist_uri(id) -> str:
    return f"youtube:playlist:{id}"


def format_channel_uri(id) -> str:
    return f"youtube:channel:{id}"


def extract_video_id(uri) -> str:
    if uri is None:
        return ""
    if "youtube.com" in uri:
        url = urlparse(uri.replace("yt:", "").replace("youtube:", ""))
        req = parse_qs(url.query)
        if "v" in req:
            video_id = req.get("v")[0]
            return video_id
    elif "youtu.be" in uri:
        url = uri.replace("yt:", "").replace("youtube:", "")
        if not re.match("^(?:http|https)://", url):
            url = "https://" + url
        video_id = urlparse(url).path
        if video_id[0] == "/":
            video_id = video_id[1:]
            return video_id
    for regex in (uri_video_regex, old_uri_video_regex):
        match = regex.match(uri)
        if match:
            return match.group("videoid")
    return ""


def extract_playlist_id(uri) -> str:
    if "youtube.com" in uri:
        url = urlparse(uri.replace("yt:", "").replace("youtube:", ""))
        req = parse_qs(url.query)
        if "list" in req:
            playlist_id = req.get("list")[0]
            return playlist_id
    for regex in (uri_playlist_regex, old_uri_playlist_regex):
        match = regex.match(uri)
        if match:
            return match.group("playlistid")
    return ""


def extract_channel_id(uri) -> str:
    for regex in (uri_channel_regex, old_uri_channel_regex):
        match = regex.match(uri)
        if match:
            return match.group("channelid")
    return ""


def extract_preload_tracks(uri) -> dict:
    match = uri_preload_regex.match(uri)
    if match:
        preload_data = json.loads(match.group("preload_data"))
        preload_tracks = [
            ytm_item_to_video(track) for track in preload_data if "videoId" in track
        ]
        return {
            "videoUri": format_video_uri(match.group("videoid")),
            "preloadTracks": preload_tracks,
        }
    return ""
