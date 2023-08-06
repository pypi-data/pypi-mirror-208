import mariadb
import json
from abc import ABC, abstractmethod
from typing import Self
from mariadb import Cursor

with open("config.json") as f:
    config = json.load(f)["db"]
DB_HOST=config["host"]
DB_USER=config["username"]
DB_PASSWORD=config["password"]
DB_PORT=config["port"]
DB_NAME=config["database"]

try:
    conn: mariadb.Connection = mariadb.connect(
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME
    )
except mariadb.Error as e:
    print(f"Error connecting to MariaDB Platform: {e}")
    quit(69)


class CustomCursor:
    def __init__(self) -> None:
        self.cursor = conn.cursor()

    def execute(self, statement, data = None):
        self.cursor.execute(
            statement, data # type: ignore
        )
        print("\n[QUERY DEBUG]: {}".format(self.cursor.statement))

    def fetchall(self):
        rows = self.cursor.fetchall()
        return rows

    def commit(self):
        conn.commit()


def get_cursor() -> Cursor:
    return conn.cursor() # type: ignore
