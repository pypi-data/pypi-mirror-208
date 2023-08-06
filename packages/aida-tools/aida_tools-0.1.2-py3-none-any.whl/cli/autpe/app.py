from argparse import ArgumentParser
from datetime import datetime

from rich.progress import track
from rich.console import Console
from rich.prompt import Prompt

from aida_tools.importer import Importer
from aida_tools.utils import safe_replace

from cli.autpe.config import MAPPING

from models.autpe import Autpe
from models.date import Date
from models.log_form import LogForm
from models.db import conn

LOG_FILE = "autpe-importer.log"

def get_args() -> bool:
    parser = ArgumentParser(
        prog="autpe-importer",
        description="Import data from CSV file to AIDA2 database"
    )
    parser.add_argument("-q","--quiet", help="Don't show debug messages", action="store_true")
    args = parser.parse_args()

    return args.quiet

def main():
    console = Console()
    log = Console(file=open(LOG_FILE, "w", encoding="utf-8"))
    counter = 0
    duplicates = 0

    quiet = get_args()

    importer = Importer("data/autpe/Copia di Anagrafiche_bonifica(266).csv", MAPPING)

    for row in track(importer.next_row(), description="[cyan]Praying it works :pray:..."):
        counter += 1

        row["published"] = safe_replace(row["published"], {"si": 1, "no": 0})
        row["is_person"] = safe_replace(row["is_person"], {"persona": 1, "ente": 0})

        try:
            autpe = Autpe(
                published=row["published"],
                is_person=int(row.get("is_person", 1)),
                first_name=row["first_name"],
                last_name=row["last_name"],
                integration=row["integration"],
                story=row["story"],
                fill_status=row["fill_status"],
                no_date=1
            )
        except Exception as e:
            log.log(f"[ERROR]      {e}")
            log.log(f"[ERROR]      {row}")
            exit(69)

        duplicate = Autpe.get_by_name(row["first_name"], row["last_name"])
        if any(duplicate):
            duplicates += 1
            log.log(f"[WARNING]    Found duplicate {row['first_name']} {row['last_name']}")
            autpe = duplicate[0]
            autpe.updated_at = datetime.now()
            autpe.story = row["story"] if autpe.story is None else autpe.story
            autpe.no_date = 0 if any([autpe.exist_dates_id, autpe.exist_to_dates_id]) else 1
            autpe.published = row["published"] if autpe.published is None else autpe.published
            autpe.integration = row["integration"] if autpe.integration is None else autpe.integration
            autpe.fill_status = row["fill_status"] if autpe.fill_status is None or autpe.fill_status == "minimo" else autpe.fill_status

        if any([row["first_name_2"], row["last_name_2"], row["integration_2"]]):
            autpe.add_name(
                first_name=row["first_name_2"],
                last_name=row["last_name_2"],
                integration=row["integration_2"],
                norm=None
            )

        for func in [row["function"], row["function_2"], row["function_3"]]:
            if func:
                autpe.add_function(func)

        if row["place_id"]:
            autpe.add_place(row["place_id"], row["place_relation_type"])

        if any([
            row["existence_from_day"],
            row["existence_from_month"],
            row["existence_from_year"],
        ]) and autpe.exist_dates_id is None:
            date_from = Date.create_date(
                row["existence_from_year"],
                row["existence_from_month"],
                row["existence_from_day"]
            )
            autpe.no_date = 0
            autpe.exist_dates_id = date_from.id

        if any([
            row["existence_to_day"],
            row["existence_to_month"],
            row["existence_to_year"],
        ]) and autpe.exist_to_dates_id is None:
            date_to = Date.create_date(
                row["existence_to_year"],
                row["existence_to_month"],
                row["existence_to_day"]
            )
            autpe.no_date = 0
            autpe.exist_to_dates_id = date_to.id

        if duplicate:
            autpe.update()
        else:
            autpe.save()

        try:
            LogForm(record_id=autpe.id, table_name="autpe").save() # type: ignore
        except Exception as e:
            console.log(f"[red]ERROR[/red] :boom: saving log form for item {autpe.id}")
            console.log(e)
            
    prompt = Prompt.ask(f"Do you want to save {counter - duplicates} new records and update {duplicates} records to the session to db? [y/n]", choices=["y", "n"], default="n")

    if prompt == "n":
        if not quiet:
            console.print("[yellow]Session not saved to db :thumbs_down:")
        exit(0)

    try:
        conn.commit()
    except Exception as e:
        if not quiet:
            console.print(f"[red][bold]An error occurred while saving the session to db: [/bold]{e} :boom:")
        log.log(f"An error occurred while saving the session to db: {e}")
        conn.rollback()
        conn.close()
        exit(69)

    conn.close()
    if not quiet:
        console.print("[green]Session saved to db :tada:")
