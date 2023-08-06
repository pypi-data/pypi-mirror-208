from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any

from models.db import get_cursor
from models.date import Date

cursor = get_cursor()
TABLE_NAME = "names"

class Names(BaseModel):
    id: Optional[int] = Field(default=None)
    pos: int = Field(default=2)
    table_name: str
    record_id: Optional[str] = Field(default=None)
    table_column: Optional[str] = Field(default=None)
    first_name: Optional[str] = Field(default=None)
    last_name: Optional[str] = Field(default=None)
    integration: Optional[str] = Field(default=None)
    norm: Optional[str] = Field(default=None)
    no_date_from: int = Field(default=0)
    no_date_to: int = Field(default=0)
    dts_from_dates_id: Optional[int] = Field(default=None)
    dts_to_dates_id: Optional[int] = Field(default=None)

    @staticmethod
    def from_list(values: list, with_id: bool = False) -> "Names":
        if with_id:
            return Names(**dict(zip(["id"] + Names._get_field_names(), values)))

        return Names(**dict(zip(Names._get_field_names(), values)))

    @staticmethod
    def _get_field_names() -> list[str]:
        return [field.name for field in Names.__fields__.values() if field.name != "id"]

    @staticmethod
    def get_all() -> list["Names"]:
        cursor.execute(f"SELECT * FROM {TABLE_NAME}")
        rows = cursor.fetchall()
        return [Names.from_list(row, with_id=True) for row in rows]

    @staticmethod
    def get_by_id(id: int) -> "Names":
        cursor.execute(f"SELECT * FROM {TABLE_NAME} WHERE id = ?", [id])
        row = cursor.fetchone()
        return Names.from_list(row, with_id=True)

    @staticmethod
    def get_by(filter_mask: Dict[str, Any]) -> List["Names"]:
        cursor.execute(f"SELECT * FROM {TABLE_NAME} WHERE {' AND '.join([f'{key} = ?' for key in filter_mask.keys()])}", list(filter_mask.values()))
        rows = cursor.fetchall()
        return [Names.from_list(row, with_id=True) for row in rows]

    def save(self) -> "Names":
        cursor.execute(
            f"INSERT INTO {TABLE_NAME} ({', '.join(self._get_field_names())}) VALUES ({', '.join(['?'] * len(self._get_field_names()))})",
            [getattr(self, field) for field in self._get_field_names()]
        )

        self.id = cursor.lastrowid

        return self