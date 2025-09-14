from dataclasses import dataclass
from datetime import datetime

@dataclass
class Club:

    id: int 
    name: str

    def params(self) -> list[str]:
        return [self.name]    
    
@dataclass
class Fixture:

    id: int
    home_club: Club
    away_club: Club
    start_time: datetime

    def params(self) -> list[str]:
        return [self.home_club.name, self.away_club.name, self.start_time]    
    
