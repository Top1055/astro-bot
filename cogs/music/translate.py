# Handles translating urls and search terms

import yt_dlp as ytdlp
import spotipy

ydl_opts = {
        'format':           'bestaudio/best',
        'quiet':            True,
        'default_search':   'ytsearch',
        'ignoreerrors':     True,
}

async def main(url, sp):

    #url = url.lower()

    # Check if link or search
    if url.startswith("https://") is False:
        return await search_song(url)

    #TODO add better regex or something
    if 'spotify' in url:
        if 'track' in url:
            return await spotify_song(url, sp)
        elif 'playlist' in url:
            return await spotify_playlist(url, sp)

    soundcloud_song = 'soundcloud' in url and 'sets' not in url
    # Not implemented yet
    # soundcloud_playlist = 'soundcloud' in url and 'sets' in url

    youtube_song = 'watch?v=' in url or 'youtu.be/' in url
    youtube_playlist = 'playlist?list=' in url

    if soundcloud_song or youtube_song:
        return await song_download(url)

    if youtube_playlist:
        return await playlist_download(url)

    return []


async def search_song(search):
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


async def spotify_song(url, sp):
        track = sp.track(url.split("/")[-1].split("?")[0])
        search = ""

        for i in track["artists"]:
            # grabs all the artists name's if there's more than one
            search = search + (i['name'] + ", ")

        # remove last comma
        search = search[:-2]

        # set search to name
        query = search + " - " + track['name']

        return await search_song(query)


async def spotify_playlist(url, sp):
    # Get the playlist uri code
    code = url.split("/")[-1].split("?")[0]

    # Grab the tracks if the playlist is correct
    try:
        results = sp.playlist_tracks(code)['items']
    except spotipy.exceptions.SpotifyException:
        return []
    
     # Go through the tracks
    songs = []
    for track in results:
        search = ""

        # Fetch all artists
        for artist in track['track']['artists']:

            # Add all artists to search
            search += f"{artist['name']}, "

        # Remove last column
        search = search[:-2]
        search += f" - {track['track']['name']}"
        songs.append(search)

        #searched_result = search_song(search)
        #if searched_result == []:
            #continue

        #songs.append(searched_result[0])
    
    while True:
        search_result = await search_song(songs[0])
        if search_result == []:
            songs.pop(0)
            continue
        else:
            songs[0] = search_result[0]
            break
    
    return songs


async def song_download(url):
    with ytdlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
        except:
            return []
    if info is None:
        return []

    data = {'url':          info['url'],
            'title':        info['title'],
            'thumbnail':    info['thumbnail'],
            'duration':     info['duration']} # Grab data
    return [data]


async def playlist_download(url):
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
