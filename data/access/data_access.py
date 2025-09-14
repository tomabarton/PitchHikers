from datetime import datetime
from data.access.db import PostgresDB
from data.google.places import Place
from data.access.singleton import Singleton
from data.entity.club import Club, Fixture
from data.entity.journey import Journey, CarJourney, CoachJourney, TrainJourney, build_journey
from data.entity.transport import Car, Coach, Train, CarEmissionType
from data.entity.user import User


class DataAccess(metaclass=Singleton):

    def __init__(self):
        self.users_cache = self.get_users()
        self.users_email_cache = {user.email: user for user in self.users_cache}  # TODO: change to user ID caching
        self.clubs_cache = self.get_clubs()
        self.clubs_mapping = self.map_clubs()
        self.fixtures_cache = self.get_fixtures()
        self.fixture_mapping = self.map_fixtures()

    def refresh_user_cache(self):
        with PostgresDB() as db:
            query = "SELECT email, id, fname, lname, date_of_birth FROM users"
            records = db.get_all(query)
            self._users = {record[0]: User(*record) for record in records}
            self._users_by_email = {user.email: user for user in self._users.values()}

    def create_user(self, user: User) -> bool:
        is_success = False
        with PostgresDB() as db:
            user_params = user.params()
            query = f"INSERT into users (id, fname, lname, date_of_birth, email) VALUES (%s, %s, %s, %s, %s)"
            is_success = db.execute_query(query, user_params)
        if is_success:
            self.users_cache.append(user)  # TODO: Handle caching in this way?
            self.users_email_cache[user.email] = user
        return is_success

    def get_users(self) -> list[User] | None:
        with PostgresDB() as db:
            query = "SELECT * FROM users"
            records = db.get_all(query)
            if not records:
                return []
            print(records)
            return [User(*record) for record in records] if records else []  # TODO: users table drop off club
        
    def delete_user(self, user_id: str) -> bool:  
        is_success = False
        with PostgresDB() as db:
            query = "SELECT delete_user(%s)"
            is_success = db.execute_query(query, [user_id])  # If __enter__ excepts then db is None 
        return is_success

    def is_existing_user(self, email: str) -> User | None:
        return self.users_email_cache.get(email, None)

    def create_club(self, club: Club) -> bool:
        is_success = False
        with PostgresDB() as db:
            club_params = club.params()
            query = "INSERT INTO clubs (name) VALUES (%s)"
            is_success = db.execute_query(query, club_params)
        return is_success

    def get_clubs(self) -> list[Club] | None:
        with PostgresDB() as db:
            query = "SELECT id, name FROM clubs"
            records = db.get_all(query)
            return [Club(*record) for record in records] if records else []
        
    def map_clubs(self) -> dict[int,Club] | None:
        return {club.id: club for club in self.clubs_cache}

    def add_supporting_club_for_user(self, user_id: int, club: Club) -> bool | None:  # TODO: Pass user obj to make inline?
        is_success = False
        with PostgresDB() as db:
            query = """
                INSERT INTO users_clubs (user_id, club_id)
                VALUES (%s, %s)
                ON CONFLICT (user_id)
                DO UPDATE SET club_id = EXCLUDED.club_id
            """
            is_success = db.execute_query(query, [user_id, club.id])
        return is_success

    def get_supporting_club_for_user(self, id: int) -> Club | None:  # TODO: Pass user obj to make inline?
        with PostgresDB() as db:
            query = """
                SELECT id, name 
                FROM clubs
                WHERE id IN (SELECT club_id 
                             FROM users_clubs 
                             WHERE user_id = %s)
            """
            record = db.get_one(query, [id])
            return Club(*record) if record else None
        
    def get_club_for_users(self) -> dict[int,Club] | None:
        with PostgresDB() as db: # TODO: figure out exact query at some point
            query = """  
                SELECT users.id, clubs.id, clubs.name
                FROM users
                JOIN clubs ON users.supporting_club = clubs.id
            """
            records = db.get_all(query)
            return {record[0]: Club(record[1], record[2]) for record in records} if records else {}

    def add_fixture(self, fixture: Fixture) -> bool:
        is_success = False
        fixture_params = fixture.params()
        with PostgresDB() as db:
            query = "INSERT INTO fixtures (home_club_id, away_club_id, start_time) VALUES (%s, %s, %s)"
            is_success = db.execute_query(query, fixture_params)
        return is_success
    
    def get_fixtures(self) -> list[Fixture] | None:
        with PostgresDB() as db:
            query = """
                SELECT 
                    f.id, 
                    f.home_club_id, 
                    hc.name AS home_club_name, 
                    f.away_club_id, 
                    ac.name AS away_club_name, 
                    f.start_time
                FROM fixtures AS f
                JOIN clubs AS hc ON f.home_club_id = hc.id
                JOIN clubs AS ac ON f.away_club_id = ac.id
            """
            records = db.get_all(query)
            fixtures: list[Fixture] = []
            for record in records:
                fixture_id: int = record[0]
                home_club: Club = Club(record[1], record[2])
                away_club: Club = Club(record[3], record[4])
                start_time = record[5]
                fixture: Fixture = Fixture(fixture_id, home_club, away_club, start_time)
                fixtures.append(fixture)
            return fixtures

    def map_fixtures(self) -> dict[int, Fixture]:
        return {fixture.id: fixture for fixture in self.fixtures_cache}


    
    def get_recent_and_upcoming_fixtures(self, club: Club) -> list[Fixture] | None:  # TODO: parameterise timeframe?
        with PostgresDB() as db:  # TODO: change to variable for time
            query = """ 
                SELECT id, home_club_id, away_club_id, start_time 
                FROM fixtures 
                WHERE (home_club_id = %s OR away_club_id = %s)
                  AND start_time > NOW() - INTERVAL '7 days'
                  AND start_time < NOW() + INTERVAL '7 days'
                ORDER BY start_time ASC
            """
            records = db.get_all(query, [club.id, club.id])
            return [Fixture(id=record[0], home_club=self.clubs_mapping[record[1]], away_club=self.clubs_mapping[record[2]], start_time=record[3]) for record in records] if records else []

    def create_journey(self, journey: Journey, user_id: int, club: Club) -> bool:
        is_success = False
        with PostgresDB() as db:
            journey_params: list[str | CarEmissionType | float | int | None] = journey.params()
            journey_params += [user_id, club.id]
            query = "SELECT insert_journey(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            is_success = db.execute_query(query, journey_params)
        return is_success
    
    def update_journey(self, journey: CarJourney | CoachJourney | TrainJourney) -> bool:
        is_success = False
        with PostgresDB() as db:
            journey_params: list[str | CarEmissionType | float | int | None] = journey.params()[1:]
            journey_params.append(journey.id)
            query = """
                UPDATE journeys 
                SET origin_id = %s, origin_address = %s, destination_id = %s, destination_address = %s, distance = %s, type = %s, green_score = %s, emission_type = %s, engine_size = %s, num_passengers = %s 
                WHERE id = %s
            """
            is_success = db.execute_query(query, journey_params)
        return is_success
    
    def delete_journey_for_user(self, journey: Journey, user_id: int) -> bool:
        is_success = False
        with PostgresDB() as db:
            query = """
                SELECT delete_journey_for_user(%s, %s)
            """
            is_success = db.execute_query(query, [journey.id, user_id])
        return is_success

    # TODO: Create generic version that returns a mpaping of users to their list of journeys
    def get_journeys_for_users(self, user_id: str) -> list[CarJourney | CoachJourney | TrainJourney] | None:
        with PostgresDB() as db:
            query = """
                SELECT uj.fixture_id, j.id, j.origin_id, j.origin_address, j.destination_id, j.destination_address, j.distance, j.type, j.emission_type, j.engine_size, j.num_passengers
                FROM journeys AS j
                JOIN users_journeys AS uj ON j.id = uj.journey_id
                WHERE uj.user_id = %s
            """
            records = db.get_all(query, [user_id])
            if not records:
                return None
            journeys: list[CarJourney | CoachJourney | TrainJourney] = []
            for record in records:  # TODO: Better way of handling all this? 
                print(record)
                transport_type: str = record[7]  # TODO: Some mapping from transport_type to python object 
                transport: Car | Coach | Train | None = None  # TODO: Should be one of these three, better way to handle if unbound?
                if transport_type == "CAR":
                    transport = Car(emission_type=record[8], engine_size=record[9])
                    num_passengers: int | None = record[10]
                if transport_type == "COACH":
                    transport = Coach()
                if transport_type == "TRAIN":
                    transport = Train()
                fixture_id: int = record[0]
                journey_id: int = record[1]
                origin: Place = Place(id=record[2], address=record[3])
                destination: Place = Place(id=record[4], address=record[5])
                distance: int = record[6]

                journey: CarJourney | CoachJourney | TrainJourney = build_journey(fixture_id, origin, destination, distance, transport, num_passengers, id=journey_id)
                journeys.append(journey)
            return journeys
    

# @dataclass
# class Car:

#     _type = "Car" # TODO: Improve this
#     nickname: str | None = None
#     emission_type: CarEmissionType | None = None
#     engine_size: float | None = None # Can be None for electric cars




    # def get_journies_for_user(self, user: User) -> Any:
    #     with PostgresDB() as db:
    #         journey_params = journey.params()
    #         columns = "origin_id, destination_id, type, green_score"
    #         values = "%s, %s, %s, %s"
    #         if isinstance(journey, CarJourney):
    #             columns += ", emission_type, engine_size, num_passengers"
    #             values += ", %s, %s, %s"
    #         query = "INSERT INTO journeys ({columns}) VALUES ({params})"
    #         is_success = db.execute_query(query, journey_params)
        
        

    #     return is_success


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

    



    

    






