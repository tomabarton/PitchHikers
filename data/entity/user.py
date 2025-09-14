from datetime import date
from dataclasses import dataclass
from enum import StrEnum
from data.access.singleton import Singleton

@dataclass
class User:

    id: int
    fname: str
    lname: str 
    date_of_birth: date
    email: str 

    def params(self) -> list[str|date]:
        return [self.id, self.fname, self.lname, self.date_of_birth, self.email]

@dataclass
class LoggedInUser(User, metaclass=Singleton):

    def logout_user(self) -> None:
        self.id = 0
        self.fname = ""
        self.lname = ""
        self.date_of_birth = date(1970, 1, 1)
        self.email = ""
