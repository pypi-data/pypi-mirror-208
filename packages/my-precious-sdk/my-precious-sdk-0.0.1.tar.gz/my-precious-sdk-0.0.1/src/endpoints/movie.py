from ..domains import Domain
from ..Session import session

class Movie(Domain):

    def __init__(
        self,
        id: str,
        name: str,
        runtimeInMinutes: int,
        budgetInMillions: int,
        boxOfficeRevenueInMillions: int,
        academyAwardNominations: int,
        academyAwardWins: int,
        rottenTomatoesScore: int,
    ):
        
        self.id = id
        self.name = name
        self.runtimeInMinutes = runtimeInMinutes
        self.budgetInMillions = budgetInMillions
        self.boxOfficeRevenueInMillions = boxOfficeRevenueInMillions
        self.academyAwardNominations = academyAwardNominations
        self.academyAwardWins = academyAwardWins
        self.rottenTomatoesScore = rottenTomatoesScore