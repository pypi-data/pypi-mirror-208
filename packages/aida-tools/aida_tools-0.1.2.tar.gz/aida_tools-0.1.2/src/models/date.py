from typing import Optional
from pydantic import BaseModel, Field

from models.db import get_cursor

cursor = get_cursor()


class Date(BaseModel):
    id: Optional[int] = Field(default=None)
    day: Optional[int] = Field(default=-1)
    exact_day: Optional[int] = Field(default=0)
    month: Optional[int] = Field(default=-1)
    # c'è un errore di battitura nel database, il campo è exact_month
    exact_mont: Optional[int] = Field(default=0)
    year: Optional[str] = Field(default='')
    exact_year: Optional[int] = Field(default=0)

    def save(self):
        cursor.execute(
            "INSERT INTO dates (day, exact_day, month, exact_mont, year, exact_year) VALUES (?, ?, ?, ?, ?, ?)",
            (self.day, self.exact_day, self.month, self.exact_mont, self.year, self.exact_year)
        )

        self.id = cursor.lastrowid

    def update(self):
        cursor.execute(
            "UPDATE dates SET day=?, exact_day=?, month=?, exact_mont=?, year=?, exact_year=? WHERE id=?",
            (self.day, self.exact_day, self.month, self.exact_mont, self.year, self.exact_year, self.id)
        )

    @staticmethod
    def _get_field_names():
        return [field.name for field in Date.__fields__.values() if field.name != "id"]

    @staticmethod
    def from_list(values: list, with_id: bool = False) -> "Date":
        """Create an Item from a list of values."""
        values = [value if isinstance(value, str) else None for value in values]
        if with_id:
            return Date(**dict(zip(["id"] + Date._get_field_names(), values)))

        return Date(**dict(zip(Date._get_field_names(), values)))

    @staticmethod
    def remove_by_id(id: int):
        cursor.execute("DELETE FROM dates WHERE id=?", (id,))

    @staticmethod
    def get_all() -> list["Date"]:
        cursor.execute("SELECT * FROM dates")
        rows = cursor.fetchall()
        return [Date.from_list(row, with_id=True) for row in rows]

    @staticmethod
    def get_by_id(id: int) -> "Date":
        cursor.execute("SELECT * FROM dates WHERE id=?", (id,))
        row = cursor.fetchone()
        return Date.from_list(row, with_id=True)

    def to_string(self) -> str | None:
        day = self.day if self.day != -1 else None
        month = self.month if self.month != -1 else None
        year = self.year if self.year != '' else None

        if all(map(lambda x: x is None, [day, month, year])):
            return None

        if day is None:
            day = "??"
        if month is None:
            month = "??"
        if year is None:
            year = "????"
        
        return f"{day}/{month}/{year}"

    @staticmethod
    def create_date(year: str | None = None, month: str | None = None, day: str | None = None) -> "Date":

        exact_year = 1
        exact_mont = 1
        exact_day = 1

        if year is not None and "[" in year:
            year = year.replace("[", "").replace("]", "")
            exact_year = 0
        if month is not None and "[" in month:
            month = month.replace("[", "").replace("]", "")
            exact_mont = 0
        if day is not None and "[" in day:
            day = day.replace("[", "").replace("]", "")
            exact_day = 0

        date = Date(
            year=year if year is not None else '',
            month=int(month) if month is not None else -1,
            day=int(day) if day is not None else -1,
            exact_year=exact_year if year is not None else 0,
            exact_mont=exact_mont if month is not None else 0,
            exact_day=exact_day if day is not None else 0
        )

        date.save()
        return date

