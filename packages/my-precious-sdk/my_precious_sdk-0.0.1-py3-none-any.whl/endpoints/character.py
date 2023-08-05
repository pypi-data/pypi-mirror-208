from ..domains import Domain
from ..Session import session

class Character(Domain):

    def __init__(
        self,
        id: str,
        height: str,
        race: str,
        gender: str,
        birth: str,
        spouse: str,
        death: str,
        realm: str,
        hair: str,
        name: str,
        wiki_url: str,
    ):

        self.id = id
        self.height = height
        self.race = race
        self.gender = gender
        self.birth = birth
        self.spouse = spouse
        self.death = death
        self.realm = realm
        self.hair = hair
        self.name = name
        self.wiki_url = wiki_url