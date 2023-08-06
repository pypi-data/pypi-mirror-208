from pydantic import BaseModel, Field
from typing import Optional, Self

from models.db import get_cursor

cursor = get_cursor()
TABLE_NAME = "attachment"

class Attachment(BaseModel):
    id: Optional[int] = Field(default=None)
    published: int = Field(default=0)
    item_id: Optional[str] = Field(default=None)
    filename: Optional[str] = Field(default=None)
    original_url: Optional[str] = Field(default=None)
    copy_url: Optional[str] = Field(default=None)
    caption: Optional[str] = Field(default=None)

    def save(self):
        cursor.execute(
            f"INSERT INTO {TABLE_NAME} (published, item_id, filename, original_url, copy_url, caption) VALUES (?, ?, ?, ?, ?, ?)",
            (self.published, self.item_id, self.filename, self.original_url, self.copy_url, self.caption)
        )
        self.id = cursor.lastrowid

    @staticmethod
    def from_list(values: list, with_id: bool = False) -> "Attachment":
        if with_id:
            return Attachment(**dict(zip(["id"] + Attachment._get_field_names(), values)))

        return Attachment(**dict(zip(Attachment._get_field_names(), values)))

    @staticmethod
    def _get_field_names() -> list[str]:
        return [field.name for field in Attachment.__fields__.values() if field.name != "id"]

    @staticmethod
    def get_all() -> list["Attachment"]:
        cursor.execute(f"SELECT * FROM {TABLE_NAME}")
        rows = cursor.fetchall()
        return [Attachment.from_list(row, with_id=True) for row in rows]

    @staticmethod
    def get_by_id(id: int) -> "Attachment":
        cursor.execute(f"SELECT * FROM {TABLE_NAME} WHERE id = ?", [id])
        row = cursor.fetchone()
        return Attachment.from_list(row, with_id=True)
