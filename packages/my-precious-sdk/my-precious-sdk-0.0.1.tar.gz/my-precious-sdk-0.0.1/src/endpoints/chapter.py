from ..domains import Domain
from ..Session import session

class Chapter(Domain):

    def __init__(self, id: str, chapterName: str, book: str):
        self.id = id
        self.chapterName = chapterName
        self._book = book