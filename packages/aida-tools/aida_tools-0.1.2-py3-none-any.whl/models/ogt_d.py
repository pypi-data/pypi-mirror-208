from pydantic import BaseModel, Field
from typing import Optional

from models.db import get_cursor

cursor = get_cursor()
TABLE_NAME = "ogt_d"

class OgtD(BaseModel):
    id: Optional[int] = Field(default=None)
    module_id: Optional[int] = Field(default=None)
    description: Optional[str] = Field(default=None)

    @staticmethod
    def from_list(values: list, with_id: bool = False) -> "OgtD":
        if with_id:
            return OgtD(**dict(zip(["id"] + OgtD._get_field_names(), values)))

        return OgtD(**dict(zip(OgtD._get_field_names(), values)))

    @staticmethod
    def _get_field_names() -> list[str]:
        return [field.name for field in OgtD.__fields__.values() if field.name != "id"]

    @staticmethod
    def get_all() -> list["OgtD"]:
        cursor.execute(f"SELECT * FROM {TABLE_NAME}")
        rows = cursor.fetchall()
        return [OgtD.from_list(row, with_id=True) for row in rows]

    @staticmethod
    def get_by_description(description: str) -> "OgtD":
        cursor.execute(f"SELECT * FROM {TABLE_NAME} WHERE description = ?", [description])
        row = cursor.fetchone()
        return OgtD.from_list(row, with_id=True)

    @staticmethod
    def get_by_id(id: int) -> "OgtD":
        cursor.execute(f"SELECT * FROM {TABLE_NAME} WHERE id = ?", [id])
        row = cursor.fetchone()
        return OgtD.from_list(row, with_id=True)
