# Handles translating urls and search terms

import yt_dlp as ytdlp

ydl_opts = {
        'format':           'bestaudio/best',
        'quiet':            True,
        'default_search':   'ytsearch',
        'ignoreerrors':     True,
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
        try:
           info = ydl.extract_info(f"ytsearch1:{search}", download=False)
        except:
            return []
    if info is None:
        return []

    info = info['entries'][0] # Get audio stream URL
    data = {'url':          info['url'],
            'title':        info['title'],
            'thumbnail':    info['thumbnail'],
            'duration':     info['duration']} # Grab data
    return [data]


def spotify_song(url):
    return []


def spotify_playlist(url):
    return []


def song_download(url):
    with ytdlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
        except:
            return []
    if info is None:
        return []

    print(info.keys())

    data = {'url':          info['url'],
            'title':        info['title'],
            'thumbnail':    info['thumbnail'],
            'duration':     info['duration']} # Grab data
    return [data]


def playlist_download(url):
    with ytdlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
        except:
            return []
    if info is None:
        return []

    info = info['entries'] # Grabbing all songs in playlist
    urls = []

    for song in info:
        data = {'url':          song['url'],
                'title':        song['title'],
                'thumbnail':    song['thumbnail'],
                'duration':     song['duration']} # Grab data
        urls.append(data)

    return urls
