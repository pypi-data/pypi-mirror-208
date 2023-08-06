from pydantic import BaseModel, Field
from typing import Optional

from models.db import get_cursor

cursor = get_cursor()
TABLE_NAME = "stcc_d"

class StccD(BaseModel):
    id: Optional[int] = Field(default=None)
    description: Optional[str] = Field(default=None)

    @staticmethod
    def from_list(values: list, with_id: bool = False) -> "StccD":
        """Create an Item from a list of values."""
        if with_id:
            return StccD(**dict(zip(["id"] + StccD._get_field_names(), values)))

        return StccD(**dict(zip(StccD._get_field_names(), values)))

    @staticmethod
    def _get_field_names() -> list[str]:
        return [field.name for field in StccD.__fields__.values() if field.name != "id"]

    @staticmethod
    def get_all() -> list["StccD"]:
        cursor.execute(f"SELECT * FROM {TABLE_NAME}")
        rows = cursor.fetchall()
        return [StccD.from_list(row, with_id=True) for row in rows]

    @staticmethod
    def get_by_description(description: str) -> "StccD":
        cursor.execute(f"SELECT * FROM {TABLE_NAME} WHERE description = ?", [description])
        row = cursor.fetchone()
        return StccD.from_list(row, with_id=True)
