from ..domains import Domain
from ..Session import session

class Quote(Domain):

    def __init__(
        self, _id: str, dialog: str, movie: str, character: str, id: str
    ):
        
        self._id = _id
        self.dialog = dialog
        self._movie = movie
        self._character = character
        self.id = id