"""
Copyright (c) 2023, Koen Martens <kmartens@sonologic.se>

Licensed under a hippocratic license. License terms can be found in
LICENSE.md or online:

https://firstdonoharm.dev/version/3/0/bds-cl-eco-extr-ffd-media-my-soc-sv-tal-xuar.md

"""
import os
import sqlite3
from pathlib import Path


class Database:
    def __init__(self, database_path: str) -> None:
        self._database_path = database_path
        self._connection = sqlite3.connect(self._database_path)
        self._create_table_if_needed()

    def _create_table_if_needed(self) -> None:
        cursor = self._connection.cursor()
        result = cursor.execute("SELECT name FROM sqlite_master WHERE name='processed'")
        if not result.fetchone():
            cursor.execute("CREATE TABLE processed(toot_id, image_url)")

    def have_processed(self, toot_id: str, image_url: str) -> None:
        cursor = self._connection.cursor()
        result = cursor.execute("SELECT * FROM processed WHERE toot_id=? and image_url=?", (toot_id, image_url))
        return result.fetchone() is not None

    def add_processed(self, toot_id: str, image_url: str) -> None:
        cursor = self._connection.cursor()
        cursor.execute("INSERT INTO processed VALUES (?, ?)", (toot_id, image_url))
        self._connection.commit()
