from data.access.db import PostgresDB
from data.access.singleton import Singleton
from data.entity.club import Club
from data.entity.user import User


class DataAccess(metaclass=Singleton):

    def __init__(self):
        self.users_cache = self.get_users()
        self.users_email_cache = [user.email for user in self.users_cache]
        self.clubs_cache = self.get_clubs()

    def create_user(self, user: User, club: Club|None) -> bool:
        is_success = False
        with PostgresDB() as db:
            club_id = club.id if club else 0
            user_params = user.params() + [club_id]
            query = f"SELECT insert_user(%s, %s, %s, %s, %s)"
            is_success = db.execute_query(query, user_params)
        return is_success

    def get_users(self) -> list[User]:
        with PostgresDB() as db:
            query = "SELECT * FROM users"
            records = db.get_all(query)
            if not records:
                return []
            print(records)
            return [User(*record) for record in records] if records else []  # TODO: users table drop off club

    def is_existing_user(self, email: str) -> bool:
        return email in [user.email for user in self.users_cache]

    def get_clubs(self) -> list[Club]:
        with PostgresDB() as db:
            query = "SELECT name, id FROM clubs"
            records = db.get_all(query)
            return [Club(*record) for record in records] if records else []

    # def get_club_supporter_num(self) -> dict[Club,int]:
    #     with PostgresDB() as db:
    #         query = """
    #             SELECT clubs.name, COUNT(user.supporting_club)
    #             FROM users
    #             JOIN clubs ON users.supporting_club = club.id
    #             GROUP BY supporting_club
    #         """
    #         records = db.get_all(query)
    #         return {record[0]: record[1] for record in records} if records else {}


    '''
    def __init__(self, db_name: str, collection: str) -> None:
        self.mongo_db = MongoDB(db_name, collection)
        assert self.mongo_db.test_connection()  # TODO: Handle retries

    def create_user_record(self, user: User) -> bool:
        return self.mongo_db.create_record(user.to_dict())

    def read_user_records(self, query: dict[str,str]={}) -> dict[str,str]:
        return self.mongo_db.read_records(query)

    # TODO: Split user and club?

    def create_club(self, club: Club) -> bool:
        return self.mongo_db.create_record(club.to_dict())

    def get_clubs(self, query: dict[str,str]={}) -> list[Club]:
        clubs_dict = self.mongo_db.read_records(query)
        clubs = [Club(club['name']) for club in clubs_dict]
        return clubs
    '''

    



    

    






