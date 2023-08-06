from pydantic import BaseModel, Field
from typing import Optional, Self

from models.db import get_cursor, CustomCursor

cursor = get_cursor()
TABLE_NAME = "autpe_has_item"

class AutpeHasItem(BaseModel):
    id: Optional[int] = Field(default=None)
    pos: int = Field(default=1)
    item_mod: str = Field(default="FOTO")
    item_column: Optional[str] = Field(default=None)
    item_id: Optional[str] = Field(default=None)
    autpe_id: Optional[str] = Field(default=None)
    autr_id: Optional[int] = Field(default=None)
    autm_id: Optional[int] = Field(default=None)
    role_str: Optional[str] = Field(default=None)
    no_date_from: int = Field(default=0)
    no_date_to: int = Field(default=0)
    dts_from_dates_id: Optional[int] = Field(default=None)
    dts_to_dates_id: Optional[int] = Field(default=None)

    @staticmethod
    def from_list(values: list, with_id: bool = False) -> "AutpeHasItem":
        """Create an Item from a list of values."""
        if with_id:
            return AutpeHasItem(**dict(zip(["id"] + AutpeHasItem._get_field_names(), values)))

        return AutpeHasItem(**dict(zip(AutpeHasItem._get_field_names(), values)))

    @staticmethod
    def _get_field_names() -> list[str]:
        return [field.name for field in AutpeHasItem.__fields__.values() if field.name != "id"]

    def save(self) -> Self:
        cursor.execute(
            f"INSERT INTO {TABLE_NAME} ({', '.join(self._get_field_names())}) VALUES ({', '.join(['?'] * len(self._get_field_names()))})",
            [getattr(self, field) for field in self._get_field_names()]
        )

        if isinstance(cursor, CustomCursor):
            self.id = cursor.cursor.lastrowid
        else:
            self.id = cursor.lastrowid

        return self

    @staticmethod
    def get_all() -> list["AutpeHasItem"]:
        cursor.execute(f"SELECT * FROM {TABLE_NAME}")
        rows = cursor.fetchall()
        return [AutpeHasItem.from_list(row, with_id=True) for row in rows]
