import deezer
from config import MAX_SEARCH_RESULTS as MSR



class Search():
    def __init__(self,modus:int,request:str):
        self.client = deezer.Client()
        self.modus = modus
        self.request = request

    def search(self) -> deezer.PaginatedList:
        while True:
            match self.modus:
                case 1: result = self.client.search(self.request)
                case 2: result = self.client.search_albums(self.request)
                case 3: result = self.client.search_artists(self.request)
            return result

    def choice(self, result: deezer.PaginatedList) -> deezer.Track:
        page_count = 0
        while True:
            for i in range(page_count*MSR,MSR+page_count*MSR):
                try:
                    match self.modus:
                        case 1: print(i+1, "|", result[i].artist.name, "-", result[i].album.title, "-", result[i].title)
                        case 2: print(i+1, "|", result[i].artist.name, "-", result[i].title)
                        case 3: print(i+1, "|", result[i].name)
                except IndexError: break
            print("---------------------------------------------------------------")
            while True:
                try:
                    index = int(input(f"View next page (0) | Enter Index for Download | "))
                    break
                except ValueError: pass
            print("---------------------------------------------------------------")
            if index == 0: page_count +=1
            else: return result[index-1]