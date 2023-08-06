from typing import Generator, Dict, Any
import csv


class Importer:

    _source: str
    _mapping: dict

    def __init__(self, source: str, mapping: dict) -> None:
        self._source = source
        self._mapping = mapping

    def next_row(self) -> Generator[Dict[str, Any], None, None]:
        with open(self._source, encoding="utf-8") as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter=';')
            mapping = self.get_field_map()
            for row in csv_reader:
                for key, value in mapping.items():
                    elem = row.pop(key)
                    row[value] = None if elem == '' else elem
                yield row
        return

    def get_field_map(self) -> Dict[str, str]:
        return self._mapping
