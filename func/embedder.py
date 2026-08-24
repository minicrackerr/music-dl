import deezer
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, APIC
import requests
from config import OUTPUT_FOLDER,illegal_characters


class Embedder():
    def __init__(self,track: deezer.Track):
        self.track = track
        self.path = f"{OUTPUT_FOLDER}/{track.artist.name}/{track.album.title}/"
        self.filename = illegal_characters(f'{track.album.artist.name} - {track.title}.mp3')

    def embed_all(self):
        self.embed_data()
        self.embed_cover()

    def embed_data(self):
        try:
            audio = EasyID3(self.path+self.filename)
            audio["albumartist"] = self.track.album.artist.name
            audio["artist"] = self.track.artist.name
            audio["album"] = self.track.album.title
            audio["title"] = self.track.title
            audio["tracknumber"] = f"{self.track.track_position}/{len(self.track.album.tracks)}"
            audio["date"] = str(self.track.release_date)
            genre = self.track.album.genres[0].name if self.track.album.genres else ""
            audio["genre"] = genre
            audio.save()
        except Exception as e:
            raise e

    def embed_cover(self):
        try:
            url = self.track.album.cover_medium
            audio = ID3(self.path+self.filename)
            audio.delall("APIC")
            audio.add(APIC(encoding=3,mime="image/jpeg",type=3,# 3 = front cover
                desc="Cover",data=requests.get(url).content))
            audio.save(v2_version=3)
        except Exception as e:
            raise e