from pydantic import BaseModel, Field
from typing import Optional

from models.db import get_cursor

cursor = get_cursor()
TABLE_NAME = "medium"

class Medium(BaseModel):
    id: Optional[int] = Field(default=None)
    module_id: Optional[int] = Field(default=None)
    description: Optional[str] = Field(default=None)

    @staticmethod
    def from_list(values: list, with_id: bool = False) -> "Medium":
        if with_id:
            return Medium(**dict(zip(["id"] + Medium._get_field_names(), values)))

        return Medium(**dict(zip(Medium._get_field_names(), values)))

    @staticmethod
    def _get_field_names() -> list[str]:
        return [field.name for field in Medium.__fields__.values() if field.name != "id"]

    @staticmethod
    def get_all() -> list["Medium"]:
        cursor.execute(f"SELECT * FROM {TABLE_NAME}")
        rows = cursor.fetchall()
        return [Medium.from_list(row, with_id=True) for row in rows]

    @staticmethod
    def get_by_description(description: str) -> "Medium":
        cursor.execute(f"SELECT * FROM {TABLE_NAME} WHERE description = ?", [description])
        row = cursor.fetchone()
        return Medium.from_list(row, with_id=True)

    @staticmethod
    def get_by_id(id: int) -> "Medium":
        cursor.execute(f"SELECT * FROM {TABLE_NAME} WHERE id = ?", [id])
        row = cursor.fetchone()
        return Medium.from_list(row, with_id=True)