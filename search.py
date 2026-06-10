import deezer
client = deezer.Client()
from config import MAX_SEARCH_RESULTS



class Search():
    def __init__(self,modus:int,request:str):
        self.modus = modus
        self.request = request
        self.index = 0
        self.pageCount = 0
        self.counter = 0

    def choice(self) -> deezer.Track:
        while self.index == 0:
            match self.modus:
                case 1: self.result = client.search(self.request)
                case 2: self.result = client.search_albums(self.request)
                case 3: self.result = client.search_artists(self.request)
            for x in range(self.pageCount,MAX_SEARCH_RESULTS+self.pageCount):
                self.counter+=1
                try:
                    match self.modus:
                        case 1: print(self.counter, "|", self.result[x].artist.name, "-", self.result[x].album.title, "-", self.result[x].title)
                        case 2: print(self.counter, "|", self.result[x].artist.name, "-", self.result[x].title)
                        case 3: print(self.counter, "|", self.result[x].name)
                except:
                    print("---- - ---- - ----")
                    break
            print("---------------------------------------------------------------")
            try:
                self.index = int(input(f"Nächsten {MAX_SEARCH_RESULTS} Titel ansehen (0) | Index Eingeben für Download | "))
            except Exception as e: print("----------ERROR||",e)
            print("---------------------------------------------------------------")
            if self.index == 0: self.pageCount += 10
            else: return self.result[self.index-1]