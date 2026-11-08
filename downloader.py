import os
import time
import yt_dlp
import deezer
from ytmusicapi import YTMusic

from config import print_log, illegal_characters, OUTPUT_FOLDER
from func.embed import Embedder



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
        yt_artist = ytm.get_artist(channelId=artist["artist_id"])
        for section in [yt_artist.get("albums"), yt_artist.get("singles")]:
            if section is None: continue
            for yt_album in Fetcher.artist_albums(ytm, section, artist["artist_id"]):
                if Fetcher.album_matches(yt_album["title"], album.title):
                    return {"state": True, "album_id": yt_album["browseId"], "deezer_album": album}
        search_results = ytm.search(query=f"{album.artist.name} {album.title}", filter="albums")
        for yt_album in search_results:
            if Fetcher.album_matches(yt_album["title"], album.title) and \
               album.artist.name.lower() in [yt_artist["name"].lower() for yt_artist in yt_album.get("artists", [])]:
                return {"state": True, "album_id": yt_album["browseId"], "deezer_album": album}
        return {"state": False, "deezer_album": album}

    def artist_albums(ytm: YTMusic, section: dict, channel_id: str) -> list:
        """
        Returns all albums of an artist section (handles pagination).
        """

        if section.get("params") is not None:
            return ytm.get_artist_albums(channelId=section.get("browseId", channel_id), params=section["params"], limit=None)
        return section.get("results", [])

    def fetch_song(track: deezer.Track) -> dict:
        """
        Takes a deezer.Track object and searches it up on YouTube.
        Returns:
            if found (dict): {"state": True, "track_id": yt_track["videoId"], "deezer_track": track}
            if not found (dict): {"state": False, "deezer_track": track}
                - state (bool):
                - track_id (str): https://www.youtube.com/watch?v={track_id}
                - deezer_track (deezer.Track):
        """

        ytm = YTMusic()
        album = Fetcher.fetch_album(album=track.album)
        if album["state"]:
            for yt_track in ytm.get_album(album["album_id"])["tracks"]:
                if yt_track.get("videoId") and Fetcher.matches(yt_track, track):
                    return {"state": True, "track_id": yt_track["videoId"], "deezer_track": track}
        search_results = ytm.search(query=f"{track.artist.name} {track.title}", filter="songs")
        for yt_track in search_results:
            if Fetcher.matches(yt_track, track):
                return {"state": True, "track_id": yt_track["videoId"], "deezer_track": track}
        return {"state": False, "deezer_track": track}

    def matches(yt_track: dict, track: deezer.Track) -> bool:
        """
        Compares a YouTube track with a Deezer track by title and duration.
        """

        if yt_track.get("title", "").lower() != track.title.lower():
            return False
        yt_seconds = Fetcher.duration_seconds(yt_track)
        if yt_seconds is None: return True
        return abs(yt_seconds - track.duration) <= 3

    def album_matches(yt_title: str, deezer_title: str) -> bool:
        """
        Compares album titles and tolerates suffixes like (Deluxe) or (Remastered).
        """

        if yt_title == deezer_title: return True
        return yt_title[:len(deezer_title)] == deezer_title

    def duration_seconds(yt_track: dict):
        """
        Returns the duration of a YouTube track in seconds.
        """

        if yt_track.get("lengthSeconds") is not None:
            return int(yt_track["lengthSeconds"])
        if yt_track.get("duration_seconds") is not None:
            return int(yt_track["duration_seconds"])
        duration = yt_track.get("duration")
        if duration and ":" in duration:
            parts = duration.split(":")
            return sum(int(part) * 60 ** (len(parts) - 1 - i) for i, part in enumerate(parts))
        return None

    def find_track(yt_tracks: list, track: deezer.Track) -> dict:
        """
        Returns the best matching usable YouTube track for a Deezer track.
        """

        fallback = None
        for yt_track in yt_tracks:
            if not yt_track.get("videoId"): continue
            if fallback is None: fallback = yt_track
            if Fetcher.matches(yt_track, track): return yt_track
        return fallback



class Downloader():
    # YT-DLP SETTINGS | generated by https://github.com/yt-dlp/yt-dlp/blob/master/devscripts/cli_to_api.py
    # OUTPUT FILE SETTINGS | https://github.com/yt-dlp/yt-dlp#output-template

    def folder(track: deezer.Track) -> str:
        """
        Returns the output folder for a track.
        """

        return f"{OUTPUT_FOLDER}/{illegal_characters(track.artist.name)}/{illegal_characters(track.album.title)}"

    def filename(track: deezer.Track) -> str:
        """
        Returns the file name (without extension) for a track.
        """

        return f"{illegal_characters(track.album.artist.name)} - {illegal_characters(track.title)}"

    def build_path(track: deezer.Track) -> str:
        """
        Returns the full file path for a track.
        """

        return f"{Downloader.folder(track)}/{Downloader.filename(track)}.mp3"

    def settings(track: deezer.Track) -> dict:
        """
        Returns a fresh yt-dlp settings dict for a track.
        """

        return {'final_ext': 'mp3', 'no_warnings': True, 'quiet': True, 'format': 'bestaudio/best', 'windowsfilenames': True,
        'paths': {'home': Downloader.folder(track)},
        'outtmpl': {'default': Downloader.filename(track)},
        'postprocessors': [{'key': 'FFmpegExtractAudio',
                            'nopostoverwrites': False,
                            'preferredcodec': 'mp3',
                            'preferredquality': '5'}]}

    def download_song(track: deezer.Track, song_id: str) -> dict:
        """
        Takes a deezer.Track object and a song_id and downloads it from YouTube as MP3.
        The metadata and the cover are embedded afterwards.
        Returns:
            if downloaded (dict): {"state": True, "deezer_track": track, "path": str}
            if failed (dict): {"state": False, "deezer_track": track}
                - state (bool):
                - deezer_track (deezer.Track):
                - path (str): full file path of the downloaded file
        """

        path = Downloader.build_path(track)
        if os.path.exists(path):
            print_log("Already Downloaded", f"{track.artist.name} - {track.title}")
            return {"state": True, "deezer_track": track, "path": path}
        print_log("Starting", f"{track.artist.name} - {track.title}")
        os.makedirs(Downloader.folder(track), exist_ok=True)
        downloader = yt_dlp.YoutubeDL(Downloader.settings(track))
        for attempt in range(5):
            try:
                downloader.download(f"https://www.youtube.com/watch?v={song_id}")
                break
            except yt_dlp.utils.DownloadError as e:
                print_log("Error", str(e))
                time.sleep(0.1)
        if not os.path.exists(path):
            print_log("Timeout", "Please retry after the process has finished")
            return {"state": False, "deezer_track": track}
        Embedder.embed_data(track=track, path=path)
        Embedder.embed_cover(track=track, path=path)
        return {"state": True, "deezer_track": track, "path": path}

    def download_playlist(album: deezer.Album, album_id: str) -> dict:
        """
        Takes a deezer.Album object and an album_id and downloads every track
        from YouTube as MP3. The metadata and the cover are embedded afterwards.
        Returns:
            (dict): {"state": bool, "deezer_album": album, "results": [result, ...]}
                - state (bool): True if every track was downloaded
                - deezer_album (deezer.Album):
                - results (list): download_song result dict for every track
        """

        ytm = YTMusic()
        yt_tracks = ytm.get_album(album_id)["tracks"]
        results = []
        for deezer_track in album.tracks:
            yt_track = Fetcher.find_track(yt_tracks, deezer_track)
            if yt_track is not None:
                yt_tracks.remove(yt_track)
            else:
                print_log("Track not Found", f"{deezer_track.artist.name} - {deezer_track.title}")
                results.append({"state": False, "deezer_track": deezer_track})
                continue
            results.append(Downloader.download_song(track=deezer_track, song_id=yt_track["videoId"]))
        return {"state": all(result["state"] for result in results), "deezer_album": album, "results": results}