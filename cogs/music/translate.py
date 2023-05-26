# Handles translating urls and search terms

import yt_dlp as ytdlp

ydl_opts = {
        'format':           'bestaudio/best',
        'quiet':            True,
        'default_search':   'ytsearch',
}

def main(url):

    #url = url.lower()

    # Check if link or search
    if url.startswith("https://") is False:
        return search_song(url)

    #TODO add better regex or something
    if 'spotify' in url:
        if 'track' in url:
            return spotify_song(url)
        elif 'playlist' in url:
            return spotify_playlist(url)

    soundcloud_song = 'soundcloud' in url and 'sets' not in url
    # Not implemented yet
    #soundcloud_playlist = 'soundcloud' in url and 'sets' in url

    youtube_song = 'watch?v=' in url or 'youtu.be/' in url
    youtube_playlist = 'playlist?list=' in url

    if soundcloud_song or youtube_song:
        return song_download(url)

    if youtube_playlist:
        return playlist_download(url)

    return []


def search_song(search):
    with ytdlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch1:{search}", download=False)
        audio_url = info['entries'][0]['url'] # Get audio stream URL
    return [audio_url]


def spotify_song(url):
    return []


def spotify_playlist(url):
    return []


def song_download(url):
    with ytdlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        audio_url = info['url'] # Get audio stream URL
    return [audio_url]


def playlist_download(url):
    return []
