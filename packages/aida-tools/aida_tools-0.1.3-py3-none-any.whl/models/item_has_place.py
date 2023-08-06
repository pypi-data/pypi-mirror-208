from pydantic import BaseModel, Field
from typing import Optional, Self

from models.db import get_cursor, CustomCursor

cursor = get_cursor()
TABLE_NAME = "item_has_place"

class ItemHasPlace(BaseModel):
    id: Optional[int] = Field(default=None)
    pos: int = Field(default=1)
    item_id: Optional[str] = Field(default=None)
    place_id: Optional[str] = Field(default=None)
    item_mod: str = Field(default="FOTO")
    item_column: str = Field(default="shooting")
    relation_type: Optional[str] = Field(default=None)

    @staticmethod
    def from_list(values: list, with_id: bool = False) -> "ItemHasPlace":
        """Create an Item from a list of values."""
        if with_id:
            return ItemHasPlace(**dict(zip(["id"] + ItemHasPlace._get_field_names(), values)))

        return ItemHasPlace(**dict(zip(ItemHasPlace._get_field_names(), values)))

    @staticmethod
    def _get_field_names() -> list[str]:
        return [field.name for field in ItemHasPlace.__fields__.values() if field.name != "id"]

    def save(self) -> Self:
        cursor.execute(
            f"INSERT INTO {TABLE_NAME} (pos, item_id, place_id, item_mod, item_column, relation_type) VALUES (?, ?, ?, ?, ?, ?)",
            (self.pos, self.item_id, self.place_id, self.item_mod, self.item_column, self.relation_type)
        )

        if isinstance(cursor, CustomCursor):
            self.id = cursor.cursor.lastrowid
        else:
            self.id = cursor.lastrowid

        return self

    @staticmethod
    def get_all() -> list["ItemHasPlace"]:
        cursor.execute(f"SELECT * FROM {TABLE_NAME}")
        rows = cursor.fetchall()
        return [ItemHasPlace.from_list(row, with_id=True) for row in rows]

    @staticmethod
    def get_by_item_id(item_id: str) -> list["ItemHasPlace"]:
        cursor.execute(f"SELECT * FROM {TABLE_NAME} WHERE item_id = ?", (item_id,))
        rows = cursor.fetchall()
        return [ItemHasPlace.from_list(row, with_id=True) for row in rows]
    