            ###-(modus,input)-> SONG CHOICE -(track,settings)-> DOWNLOAD -(track,settings)-> METADATA
            ### settings: [path]

from search import Search
from yt import Downloader
from config import print_log,illegal_characters, OUTPUT_FOLDER

import deezer
import os
from pathlib import Path
path = Path(__file__).resolve().parent
os.chdir(path=path)

settings={"path":f"{OUTPUT_FOLDER}/"}

def download_and_embed(track: deezer.Track,settings: dict=settings):
    if not os.listdir(settings['path']).count(illegal_characters(f"{track.artist.name} - {track.title}.mp3")) == 0:
        return print_log("Already Downloaded",track.title)
    print_log("Starting",track.title)
    downloader = Downloader(track=track,settings=settings)
    downloaded = downloader.download()
    if downloaded == False:
        return
    downloader.embed_data()
    downloader.embed_cover()
    print_log("Downloaded",track.title)
    print(f"------------------------------------------------------")

def download_track(result: deezer.Track):
    download_and_embed(track=result,)

def download_album(result: deezer.Album):
    artistFolder = illegal_characters(result.artist.name)
    albumFolder = illegal_characters(','.join([artist.name for artist in result.contributors])+" - "+result.title).replace(".","")
    if os.listdir(f"{OUTPUT_FOLDER}").count(artistFolder) == 0: #? artist in /{OUTPUT_FOLDER}/ -(false)-> make album dir
        os.makedirs(f"{OUTPUT_FOLDER}/{artistFolder}")
    if os.listdir(f"{OUTPUT_FOLDER}/{artistFolder}").count(albumFolder) == 0: #? album in {OUTPUT_FOLDER}/ -(false)-> make album dir
        os.makedirs(f"{OUTPUT_FOLDER}/{artistFolder}/{albumFolder}")
    settings.update({"path":f"{OUTPUT_FOLDER}/{artistFolder}/{albumFolder}/"})
    for track in result.tracks:
        download_and_embed(track=track,settings=settings)
    settings.update({"path":f"{OUTPUT_FOLDER}/"})

def download_artist(result: deezer.Artist):
     for album in result.get_albums():
        download_album(album)


while True:
    try:
        print("---------------------------------------------------------------")
        modus = int(input("Quit (0) | Song (1) | Album (2) | Artist (3) | "))
        if modus == 0: break
        userInput = input("Was willst du suchen | ")
        print("---------------------------------------------------------------")
        if modus in range(1,4):
            search = Search(modus=modus, request=userInput)
            result = search.choice()

            if isinstance(result, deezer.Track): download_track(result)
            elif isinstance(result, deezer.Album): download_album(result)
            elif isinstance(result, deezer.Artist): download_artist(result)
            else: print(type(result))
    except Exception as e: print(">>> ERROR || ",e)