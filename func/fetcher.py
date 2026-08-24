import deezer
from ytmusicapi import YTMusic

from config import print_log, OUTPUT_FOLDER

class Fetcher():

    def fetch_artist(artist: deezer.Artist) -> dict:
        """
        Takes a deezer.Artist object and searches it up on YouTube.
        Returns:
            if found (dict): {"state": True, "artist_id": yt_artist["browseId"], "deezer_artist": artist}
            if not found (dict): {"state": False, "deezer_artist": artist}
                - state (bool):
                - artist_id (str): https://www.youtube.com/channel/{artist_id}
                - deezer_artist (deezer.Artist): 
        """

        ytm = YTMusic()
        search_results = ytm.search(query=artist.name, filter="artists")
        for yt_artist in search_results:
            if artist.name == yt_artist["artist"]: 
                return {"state": True, "artist_id": yt_artist["browseId"], "deezer_artist": artist}
            else: 
                return {"state": False, "deezer_artist": artist}


    def fetch_album(album: deezer.Album) -> dict:
        """
        Takes a deezer.Album object and searches it up on YouTube.
        Returns:
            if found (dict): {"state": True, "album_id": yt_album["browseId"], "deezer_album": album}
            if not found (dict): {"state": False, "deezer_album": album}
                - state (bool):
                - album_id (str): https://www.youtube.com/playlist?list={album_id}
                - deezer_album (deezer.Album):
        """

        ytm = YTMusic()
        artist = Fetcher.fetch_artist(artist=album.artist)
        if not artist["state"]: return {"state": False, "deezer_album": album}
        #yt_albums = ytm.get_artist(channelId=artist["artist_id"])["albums"]["results"]
        yt_artist = ytm.get_artist(channelId=artist["artist_id"])["albums"]
        if not yt_artist.get("params") == None:
            yt_albums = ytm.get_artist_albums(channelId=yt_artist["browseId"], params=yt_artist["params"], limit=None)
        else: yt_albums = yt_artist["results"]
        for yt_album in yt_albums:
            print(yt_album["title"])
            if yt_album["title"] == album.title:
                return {"state": True, "album_id": yt_album["browseId"], "deezer_album": album}
            # (deluxe/remastered) ?
            # elif yt_album["title"][:len(album.title)] == album.title: 
            #     return {"state": True,"album_id": yt_album["browseId"],"deezer_album": album}
        print("Album GRRR")  
        return {"state": False, "deezer_album": album}

    def fetch_song(track: deezer.Track):
        """
        Takes a deezer.Track object and searches artist it up on YouTube.
        Returns:
            if found (dict): {"state": True, "track_id": yt_track["browseId"], "deezer_track": track}
            if not found (dict): {"state": False, "deezer_track": track}
                - state (bool):
                - track_id (str): https://www.youtube.com/watch?v={track_id}
                - deezer_track (deezer.Track):
        """

        ytm = YTMusic()
        yt_tracks = ytm.search(query=f"{track.title} - {track.artist.name}",filter="songs")
        for yt_track in yt_tracks:
            if yt_track["title"] == track.title and yt_track["album"]["name"] == track.album.title:
                return {"state": True, "track_id": yt_track["videoId"], "deezer_track": track}
        else:
            return {"state": False, "deezer_track": track}