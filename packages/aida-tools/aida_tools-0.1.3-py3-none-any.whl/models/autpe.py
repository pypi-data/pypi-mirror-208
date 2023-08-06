from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

from models.db import get_cursor
from models.autpe_has_place import AutpeHasPlace
from models.mult_value import MultValue
from models.date import Date
from models.names import Names
from aida_tools.utils import generate_id

cursor = get_cursor()
TABLE_NAME = "autpe"

class Autpe(BaseModel):
    id: str = Field(default_factory=generate_id)
    published: Optional[int] = Field(default=None)
    is_person: int = Field(default=0)
    first_name: Optional[str] = Field(default=None)
    last_name: Optional[str] = Field(default=None)
    integration: Optional[str] = Field(default=None)
    norm: Optional[str] = Field(default=None)
    val_from_dates_id: Optional[int] = Field(default=None)
    val_to_dates_id: Optional[int] = Field(default=None)
    par_name: Optional[str] = Field(default=None)
    par_surname: Optional[str] = Field(default=None)
    par_integration: Optional[str] = Field(default=None)
    par_norm: Optional[str] = Field(default=None)
    par_val_from_dates_id: Optional[int] = Field(default=None)
    par_val_to_dates_id: Optional[int] = Field(default=None)
    no_date: Optional[int] = Field(default=0)
    exist_dates_id: Optional[int] = Field(default=None)
    exist_to_dates_id: Optional[int] = Field(default=None)
    story: Optional[str] = Field(default=None)
    function: Optional[str] = Field(default=None)
    aut_place_ids: Optional[str] = Field(default=None)
    aut_place_dist_ids: Optional[str] = Field(default=None)
    code_auth: Optional[str] = Field(default=None)
    institution: Optional[str] = Field(default=None)
    link: Optional[str] = Field(default=None)
    sources: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    created_by: Optional[str] = Field(default=None)
    updated_by: Optional[str] = Field(default=None)
    operation: Optional[str] = Field(default=None)
    status_id: Optional[int] = Field(default=None)
    fill_status: Optional[str] = Field(default="parziale")

    @staticmethod
    def from_list(values: List, with_id: bool = False) -> "Autpe":
        if with_id:
            return Autpe(**dict(zip(["id"] + Autpe._get_field_names(), values)))

        return Autpe(**dict(zip(Autpe._get_field_names(), values)))

    @staticmethod
    def _get_field_names() -> List[str]:
        return [field.name for field in Autpe.__fields__.values() if field.name != "id"]

    @staticmethod
    def get_all() -> List["Autpe"]:
        cursor.execute(f"SELECT * FROM {TABLE_NAME}")
        rows = cursor.fetchall()
        return [Autpe.from_list(row, with_id=True) for row in rows]

    @staticmethod
    def get_by_id(id: int) -> "Autpe":
        cursor.execute(f"SELECT * FROM {TABLE_NAME} WHERE id = ?", [id])
        row = cursor.fetchone()
        return Autpe.from_list(row, with_id=True)

    @staticmethod
    def get_by_name(first_name: str, last_name: str) -> List["Autpe"]:
        cursor.execute(f"SELECT * FROM {TABLE_NAME} WHERE first_name = ? AND last_name = ?", [first_name, last_name])
        rows = cursor.fetchall()
        return [Autpe.from_list(row, with_id=True) for row in rows]

    def save(self) -> "Autpe":
        values = [getattr(self, field.name) for field in self.__fields__.values()]

        cursor.execute(
            "INSERT INTO {} ({}) VALUES ({})".format(
                TABLE_NAME,
                ", ".join(["id"] + self._get_field_names()),
                ", ".join(["?"] * (len(self._get_field_names()) + 1))),
            values
        )

        return self

    def add_place(self, place_id: str, relation_type: Optional[str]) -> "Autpe":
        places = AutpeHasPlace.get_by_autpe_id(self.id)
        for place in places:
            if place.place_id == place_id and str(place.relation_type).strip().lower() == str(relation_type).strip().lower():
                return self
        try:
            old_pos = max([row.pos for row in places])
        except ValueError:
            old_pos = 0
        AutpeHasPlace(
            pos=old_pos + 1,
            autpe_id=self.id,
            place_id=place_id,
            relation_type=relation_type,
            no_date_from=1,
            no_date_to=1
        ).save()
        return self

    def add_function(self, function: str) -> "Autpe":
        if self.function is None:
            self.function = function
        if self.function == function:
            return self
        else:
            try:
                functions = MultValue.get_by({
                    "table_name": TABLE_NAME,
                    "record_id": self.id,
                    "table_column": "function"
                })
                for func in functions:
                    if func.str_value == function:
                        return self
                old_pos = max([row.pos for row in functions])
            except ValueError:
                old_pos = 1
            MultValue(
                table_name=TABLE_NAME,
                pos=old_pos + 1,
                record_id=self.id,
                table_column="function",
                type="string",
                str_value=function
            ).save()

        return self

    def add_place_with_date(self, place_id: str, date_id: int, relation_type: Optional[str]) -> "Autpe":
        try:
            places = AutpeHasPlace.get_by_autpe_id(self.id)
            for place in places:
                if place.place_id == place_id and place.relation_type == relation_type:
                    return self
            old_pos = max([row.pos for row in places])
        except ValueError:
            old_pos = 0
        AutpeHasPlace(
            pos=old_pos + 1,
            autpe_id=self.id,
            place_id=place_id,
            from_dates_id=date_id,
            to_dates_id=date_id
        ).save()
        return self

    def add_name(
            self,
            first_name: Optional[str],
            last_name: Optional[str],
            integration: Optional[str],
            norm: Optional[str]
        ) -> "Autpe":
        if first_name is None and last_name is None and integration is None and norm is None:
            return self
        if self.first_name == first_name and self.last_name == last_name and self.integration == integration and self.norm == norm:
            return self
        if any([first_name, last_name, integration, norm]) and not all([first_name, last_name, integration, norm]):
            self.first_name = first_name
            self.last_name = last_name
            self.integration = integration
            self.norm = norm
            return self

        try:
            names = Names.get_by({
                "table_name": TABLE_NAME,
                "record_id": self.id,
                "table_column": "auth"
            })
            for name in names:
                if name.first_name == first_name and name.last_name == last_name and name.integration == integration and name.norm == norm:
                    return self
            old_pos = max([row.pos for row in names])
        except ValueError:
            old_pos = 1
        Names(
            table_name=TABLE_NAME,
            pos=old_pos + 1,
            record_id=self.id,
            table_column="auth",
            first_name=first_name,
            last_name=last_name,
            integration=integration,
            norm=norm,
            no_date_from=1,
            no_date_to=1
        ).save()

        return self

    def add_name_with_date(
            self,
            first_name: Optional[str],
            last_name: Optional[str],
            integration: Optional[str],
            norm: Optional[str],
            from_date: Date,
            to_date: Date
        ) -> "Autpe":

        if first_name is None and last_name is None and integration is None and norm is None:
            return self
        if any([first_name, last_name, integration, norm, from_date, to_date]):
            self.first_name = first_name
            self.last_name = last_name
            self.integration = integration
            self.norm = norm
            self.val_from_dates_id = from_date.id
            self.val_to_dates_id = to_date.id
            return self
        
        try:
            names = Names.get_by({
                "table_name": TABLE_NAME,
                "record_id": self.id,
                "table_column": "auth"
            })
            for name in names:
                if name.first_name == first_name and name.last_name == last_name and name.integration == integration and name.norm == norm:
                    return self
            old_pos = max([row.pos for row in names])
        except ValueError:
            old_pos = 1
        Names(
            table_name=TABLE_NAME,
            pos=old_pos + 1,
            record_id=self.id,
            table_column="auth",
            first_name=first_name,
            last_name=last_name,
            integration=integration,
            norm=norm,
            dts_from_dates_id=from_date.id,
            dts_to_dates_id=to_date.id
        ).save()

        return self

    def update(self) -> "Autpe":
        cursor.execute(
            f"UPDATE {TABLE_NAME} SET {', '.join([f'{field} = ?' for field in self._get_field_names()])} WHERE id = ?",
            [getattr(self, field) for field in self._get_field_names()] + [self.id]
        )

        return self
