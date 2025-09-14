from data.access.db import PostgresDB
from data.entity.transport import CarEmissionType, Car, Coach, Train

class DataAccessTransport:

    def __init__(self):
        self.users_transport_cache = self.get_transports_for_users()

    def get_transports_for_users(self) -> dict[int, list[Car | Coach | Train]] | None:
        with PostgresDB() as db:
            query = """
                SELECT ut.user_id, t.id, t.type, t.emission_type, t.engine_size
                FROM user_transports ut
                JOIN transports t ON ut.transport_id = t.id
            """
            records = db.get_all(query)
            if not records:
                return {}
            transport_dict: dict[int, list[Car | Coach | Train]] = {}
            for record in records:
                user_id = record[0]
                transport_id = record[1]
                transport_type = record[2]
                emission_type = record[3]
                engine_size = record[4]

                if transport_type == 'CAR':
                    transport = Car(id=transport_id, emission_type=CarEmissionType[emission_type], engine_size=engine_size)
                elif transport_type == 'COACH':
                    transport = Coach(id=transport_id)
                elif transport_type == 'TRAIN':
                    transport = Train(id=transport_id)
                else:
                    continue