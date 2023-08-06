from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

from models.db import get_cursor

cursor = get_cursor()
TABLE_NAME = "folder"

class Folder(BaseModel):
    id: Optional[str] = Field(default=None)
    parent_id: Optional[str] = Field(default=None)
    level_id: int
    published: int = Field(default=0)
    denomination: str
    initials: str = Field(max_length=3)
    no_date: int = Field(default=0)
    dts_from_dates_id: Optional[int] = Field(default=None)
    dts_to_dates_id: Optional[int] = Field(default=None)
    medium_id: Optional[int] = Field(default=None)
    num_support: Optional[int] = Field(default=None)
    placing: Optional[str] = Field(default=None)
    story: Optional[str] = Field(default=None)
    story_archive: Optional[str] = Field(default=None)
    acquisition: Optional[str] = Field(default=None)
    ambit: Optional[str] = Field(default=None)
    increase: Optional[str] = Field(default=None)
    sort_criterion: Optional[str] = Field(default=None)
    access_conditions: Optional[str] = Field(default=None)
    note: Optional[str] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    created_by: Optional[int] = Field(default=None)
    updated_by: Optional[int] = Field(default=None)
    operation: Optional[str] = Field(default=None)
    status_id: Optional[int] = Field(default=None)
    fill_status: Optional[str] = Field(default=None)

    @staticmethod
    def from_list(values: list, with_id: bool = False) -> "Folder":
        if with_id:
            return Folder(**dict(zip(["id"] + Folder._get_field_names(), values)))

        return Folder(**dict(zip(Folder._get_field_names(), values)))

    @staticmethod
    def _get_field_names() -> list[str]:
        return [field.name for field in Folder.__fields__.values() if field.name != "id"]

    @staticmethod
    def get_all() -> list["Folder"]:
        cursor.execute(f"SELECT * FROM {TABLE_NAME}")
        rows = cursor.fetchall()
        return [Folder.from_list(row, with_id=True) for row in rows]

    @staticmethod
    def get_by_name(description: str) -> "Folder":
        cursor.execute(f"SELECT * FROM {TABLE_NAME} WHERE denomination = ?", [description])
        row = cursor.fetchone()
        return Folder.from_list(row, with_id=True)

    @staticmethod
    def get_by_id(id: int) -> "Folder":
        cursor.execute(f"SELECT * FROM {TABLE_NAME} WHERE id = ?", [id])
        row = cursor.fetchone()
        return Folder.from_list(row, with_id=True)