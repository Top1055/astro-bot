# Handles translating urls and search terms

def main(url):

    url = url.lower()

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
    soundcloud_playlist = 'soundcloud' in url and 'sets' in url

    youtube_song = 'watch?v=' in url or 'youtu.be/' in url
    youtube_playlist = 'playlist?list=' in url

    if soundcloud_song or youtube_song:
        return song_download(url)

    if youtube_playlist:
        return playlist_download(url)

    return False


def search_song(search):
    return None


def spotify_song(url):
    return None


def spotify_playlist(url):
    return None


def song_download(url):
    return None


def playlist_download(url):
    return None
