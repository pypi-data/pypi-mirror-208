from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

from models.db import get_cursor

cursor = get_cursor()
TABLE_NAME = "log_form"

class LogForm(BaseModel):
    id: Optional[int] = Field(default=None)
    user_id: str = Field(default="rootuser")
    table_name: str = Field(default="item")
    record_id: str
    event_type: str = Field(default="import")
    event_date: datetime = Field(default_factory=datetime.now)

    @staticmethod
    def from_list(values: list, with_id: bool = False) -> "LogForm":
        if with_id:
            return LogForm(**dict(zip(["id"] + LogForm._get_field_names(), values)))

        return LogForm(**dict(zip(LogForm._get_field_names(), values)))

    @staticmethod
    def _get_field_names() -> list[str]:
        return [field.name for field in LogForm.__fields__.values() if field.name != "id"]

    @staticmethod
    def get_all() -> list["LogForm"]:
        cursor.execute(f"SELECT * FROM {TABLE_NAME}")
        rows = cursor.fetchall()
        return [LogForm.from_list(row, with_id=True) for row in rows]

    @staticmethod
    def get_by_id(id: int) -> "LogForm":
        cursor.execute(f"SELECT * FROM {TABLE_NAME} WHERE id = ?", [id])
        row = cursor.fetchone()
        return LogForm.from_list(row, with_id=True)

    def save(self) -> "LogForm":
        cursor.execute(
            f"INSERT INTO {TABLE_NAME} ({', '.join(self._get_field_names())}) VALUES ({', '.join(['?'] * len(self._get_field_names()))})",
            [getattr(self, field) for field in self._get_field_names()]
        )

        self.id = cursor.lastrowid

        return self
