from pydantic import BaseModel, Field
from typing import Optional, List

from models.db import get_cursor

cursor = get_cursor()
TABLE_NAME = "mult_value"

class MultValue(BaseModel):
    id: Optional[int] = Field(default=None)
    pos: int = Field(default=2)
    table_name: str
    record_id: Optional[str] = Field(default=None)
    table_column: Optional[str] = Field(default=None)
    type: str = Field(default="string")
    str_value: Optional[str] = Field(default=None)
    int_value: Optional[int] = Field(default=None)
    dates_id: Optional[int] = Field(default=None)


    @staticmethod
    def from_list(values: list, with_id: bool = False) -> "MultValue":
        if with_id:
            return MultValue(**dict(zip(["id"] + MultValue._get_field_names(), values)))

        return MultValue(**dict(zip(MultValue._get_field_names(), values)))

    @staticmethod
    def _get_field_names() -> List[str]:
        return [field.name for field in MultValue.__fields__.values() if field.name != "id"]

    @staticmethod
    def get_all() -> List["MultValue"]:
        cursor.execute(f"SELECT * FROM {TABLE_NAME}")
        rows = cursor.fetchall()
        return [MultValue.from_list(row, with_id=True) for row in rows]

    @staticmethod
    def get_by_id(id: int) -> "MultValue":
        cursor.execute(f"SELECT * FROM {TABLE_NAME} WHERE id = ?", [id])
        row = cursor.fetchone()
        return MultValue.from_list(row, with_id=True)

    @staticmethod
    def get_by(filter_mask: dict) -> List["MultValue"]:
        cursor.execute(f"SELECT * FROM {TABLE_NAME} WHERE {' AND '.join([f'{key} = ?' for key in filter_mask.keys()])}", list(filter_mask.values()))
        rows = cursor.fetchall()
        return [MultValue.from_list(row, with_id=True) for row in rows]

    def save(self) -> "MultValue":
        cursor.execute(
            f"INSERT INTO {TABLE_NAME} ({', '.join(self._get_field_names())}) VALUES ({', '.join(['?'] * len(self._get_field_names()))})",
            [getattr(self, field) for field in self._get_field_names()]
        )

        self.id = cursor.lastrowid

        return self
