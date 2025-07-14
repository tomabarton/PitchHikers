from datetime import date
import psycopg2
from types import TracebackType
from typing import Optional, Type, Any
from utils.log import log


class PostgresDB:

    def __init__(
            self, 
            dbname: str="PitchHikers", 
            user: str="postgres", 
            password: str="password",
            host: str='localhost', 
            port: int=5432
        ):
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        self.port = port

    def __enter__(self):
        try:
            self.connection = psycopg2.connect(
                dbname=self.dbname,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port
            )
            self.cursor = self.connection.cursor()
            return self
        except (Exception, psycopg2.DatabaseError) as e:
            print(e)
            log.error(f"Error connecting to the database: {e}")

    def __exit__(
        self, 
        exc_type: Optional[Type[BaseException]], 
        exc_value: Optional[BaseException], 
        traceback: Optional[TracebackType]
    ):
        self.cursor.close()
        self.connection.close()

    def execute_query(
            self, 
            query: str, 
            params: list[str|date|int|None] | None=None
        ) -> bool:
        try:
            self.cursor.execute(query, params)
            self.connection.commit()
            return True
        except (Exception, psycopg2.DatabaseError) as e:
            print(e)
            log.error(f"Error commiting to the database: {e}")
            return False

    def get_one(
            self, 
            query: str, 
            params: dict[str,str] | None=None
        ) -> tuple[Any] | None:
        try:
            self.cursor.execute(query, params)
            result: tuple[Any] | None = self.cursor.fetchone()
            return result[0]
        except (Exception, psycopg2.DatabaseError) as e:
            log.error(f"Error fetching one record from the database: {e}")
            return None
    
    def get_all(
            self, 
            query: str, 
            params: dict[str,str] | None=None
        ) -> list[tuple[Any]] | None:
        self.cursor.execute(query, params)
        return self.cursor.fetchall()
