from pydantic import BaseModel, Field
from typing import Optional

from models.db import get_cursor
from models.date import Date

cursor = get_cursor()
TABLE_NAME = "autpe_has_place"

class AutpeHasPlace(BaseModel):
    id: Optional[int] = Field(default=None)
    autpe_id: str
    place_id: str
    pos: int
    relation_type: Optional[str] = Field(default=None)
    no_date_from: Optional[int] = Field(default=0)
    no_date_to: Optional[int] = Field(default=0)
    from_dates_id: Optional[int] = Field(default=None)
    to_dates_id: Optional[int] = Field(default=None)

    @staticmethod
    def from_list(values: list, with_id: bool = False) -> "AutpeHasPlace":
        if with_id:
            return AutpeHasPlace(**dict(zip(["id"] + AutpeHasPlace._get_field_names(), values)))

        return AutpeHasPlace(**dict(zip(AutpeHasPlace._get_field_names(), values)))

    @staticmethod
    def _get_field_names() -> list[str]:
        return [field.name for field in AutpeHasPlace.__fields__.values() if field.name != "id"]

    @staticmethod
    def get_all() -> list["AutpeHasPlace"]:
        cursor.execute(f"SELECT * FROM {TABLE_NAME}")
        rows = cursor.fetchall()
        return [AutpeHasPlace.from_list(row, with_id=True) for row in rows]

    @staticmethod
    def get_by_id(id: int) -> "AutpeHasPlace":
        cursor.execute(f"SELECT * FROM {TABLE_NAME} WHERE id = ?", [id])
        row = cursor.fetchone()
        return AutpeHasPlace.from_list(row, with_id=True)

    @staticmethod
    def get_by_autpe_id(autpe_id: str) -> list["AutpeHasPlace"]:
        cursor.execute(f"SELECT * FROM {TABLE_NAME} WHERE autpe_id = ?", [autpe_id])
        rows = cursor.fetchall()
        if rows is None:
            return []
        return [AutpeHasPlace.from_list(row, with_id=True) for row in rows]

    def add_date(self, date_from: Optional[Date], date_to: Optional[Date]) -> "AutpeHasPlace":
        if date_from is not None:
            date_from.save()
            self.from_dates_id = date_from.id
        if date_to is not None:
            date_to.save()
            self.to_dates_id = date_to.id
        return self

    def save(self) -> "AutpeHasPlace":
        cursor.execute(
            f"INSERT INTO {TABLE_NAME} ({', '.join(self._get_field_names())}) VALUES ({', '.join(['?'] * len(self._get_field_names()))})",
            [getattr(self, field) for field in self._get_field_names()]
        )

        self.id = cursor.lastrowid

        return self
