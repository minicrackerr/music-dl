import os
import deezer
from func.search import Search
from func.downloader import Downloader
from func.fetcher import Fetcher
from func.embedder import Embedder
from config import print_log, OUTPUT_FOLDER,illegal_characters

def download_track(track: deezer.Track):
    #track_path = f"{illegal_characters(OUTPUT_FOLDER)}/{illegal_characters(track.artist.name)}/{illegal_characters(track.artist.name)} - {illegal_characters(track.album.title)}/{illegal_characters(track.album.artist.name)} - {illegal_characters(track.title)}.mp3"
    file_path = f"{OUTPUT_FOLDER}/{illegal_characters(track.artist.name)}/{illegal_characters(track.artist.name)} - {illegal_characters(track.album.title)}/"
    file_name = f"{illegal_characters(track.album.artist.name)} - {illegal_characters(track.title)}.mp3"
    track_path = [file_path, file_name]
    if os.path.exists(file_path+file_name):
        print_log("Song already downloaded", f"{track.artist.name} - {track.album.title} - {track.title}")
        return

    yt_result = Fetcher.fetch_song(track=track)
    if yt_result["state"]:
        print_log("Track found", f'{track.artist.name} - {track.title} - https://www.youtube.com/watch?v={yt_result["track_id"]}')
    else:
        print_log("Track not found", f'{track.artist.name} - {track.title}')
        return

    download_result = Downloader.download_song(track=track, song_id=yt_result["track_id"], track_path=track_path)
    if download_result["state"]: 
        print_log("Downloaded", f'{track.artist.name} - {track.title}')
    else:
        print_log("Download failed", f'{track.artist.name} - {track.title}')
        return

    Embedder(track=track, track_path=track_path).embed_all()

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
            download_track(track=deezer_result)
        case 2:
            for track in deezer_result.tracks:
                download_track(track)
        case 3: 
            deezer_result: deezer.Artist
            for album in deezer_result.get_albums():
                for track in album.tracks:
                    download_track(track)