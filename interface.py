import os
import deezer
from func.search import Search
from func.downloader import Downloader
from func.fetcher import Fetcher
from func.embedder import Embedder
from config import print_log, OUTPUT_FOLDER,illegal_characters

def download_track(deezer_result: deezer.Track):
    song_path = f"{OUTPUT_FOLDER}/{deezer_result.artist.name}/{track.artist.name} - {track.album.title}/{illegal_characters(f'{deezer_result.album.artist.name} - {deezer_result.title}.mp3')}"
    if os.path.exists(song_path):
        print_log("Song already Downloaded", f"{deezer_result.artist.name} - {deezer_result.album.title} - {deezer_result.title}")
        return

    yt_result = Fetcher.fetch_song(track=deezer_result)
    if yt_result["state"]: print_log("Found Track", f'{deezer_result.artist.name} - {deezer_result.title} - https://www.youtube.com/watch?v={yt_result["track_id"]}')
    else:
        print_log("Found not Track", f'{deezer_result.artist.name} - {deezer_result.title}')
        return

    download_result = Downloader.download_song(track=deezer_result,song_id=yt_result["track_id"])
    if download_result["state"]: print_log("Downloaded", f'{deezer_result.artist.name} - {deezer_result.title}')
    else:
        print_log("Downloaded", f'{deezer_result.artist.name} - {deezer_result.title}')
        return

    Embedder(track=deezer_result).embed_all()

while True:
    print("---------------------------------------------------------------")
    while True:
        try: 
            modus = int(input("Quit (0) | Song (1) | Album (2) | Artist (3) | "))
            if modus in range(0,4): break
        except ValueError: pass
    if modus == 0: break

    while True:
        userInput = input("What do you want to search for | ")
        if not userInput == "": break
    print("---------------------------------------------------------------")

    search = Search(modus=modus, request=userInput)
    deezer_result = search.choice(result=search.search())

    match modus:
        case 1:
            download_track(deezer_result=deezer_result)
        case 2:
            for track in deezer_result.tracks:
                download_track(track)
        case 3: 
            deezer_result: deezer.Artist
            for album in deezer_result.get_albums():
                for track in album.tracks:
                    download_track(track)