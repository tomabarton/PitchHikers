from datetime import date
from dataclasses import dataclass

@dataclass
class User:

    id: int | None
    fname: str
    lname: str 
    date_of_birth: date
    email: str 

    def params(self) -> list[str|date]:
        return [self.fname, self.lname, self.date_of_birth, self.email]

    # def to_db(self) -> str:
    #     query = """
    #             INSERT INTO users (fname, lname, date_of_birth, email)
    #             VALUES (%s, %s, %s, %s);
    #             insert into select id from users where fname = %s and lname = %s and date_of_birth = %s and email = %s;
    #         """
        