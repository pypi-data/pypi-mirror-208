from ..domains import Domain
from ..Session import session

class Book(Domain):

    def __init__(self, id: str, name: str):

        self.id = id
        self.name = name