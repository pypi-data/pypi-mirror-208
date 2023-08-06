from argparse import ArgumentParser
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from rich.progress import track
import json
import shutil
import os
import mariadb

from aida_tools.importer import Importer
from models.db import conn, get_cursor
from models.item import Item
from models.item_has_place import ItemHasPlace
from models.autpe_has_item import AutpeHasItem
from models.ogt_d import OgtD
from models.date import Date
from models.folder import Folder
from models.attachment import Attachment
from models.log_form import LogForm
from cli.tommasoli.config import MAPPING

LOG_FILE = "aida2-importer.log"


def get_args() -> tuple[str, str]:
    parser = ArgumentParser(
        prog="aida2-importer",
        description="Import data from CSV file to AIDA2 database"
    )
    parser.add_argument("-f","--file", help="File to import", required=True)
    parser.add_argument("-q","--quiet", help="Don't show debug messages", action="store_true")
    args = parser.parse_args()

    return args.file, args.quiet


def safe_replace(item, obj: dict):
    for key, value in obj.items():
        if item == key:
            return value


def create_date(year: str | None = None, month: str | None = None, day: str | None = None) -> Date | None:

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


def verify_photo_number() -> list[str]:
    with open("config.json") as json_file:
        config = json.load(json_file)["foto_dir"]

    src_folder: str = config["source"]
    dst_folder: str = config["output"]

    src_files = [elem.split(".")[0] for elem in os.listdir(src_folder)]
    dst_files = [elem.split(".")[0] for elem in os.listdir(dst_folder)]

    file_diff = list(set(src_files) - set(dst_files))
    return file_diff


def get_id_from_description(description: str | None, table: str, logger: Console):
    if description is None:
        return None

    try:
        cur = get_cursor()
        cur.execute(f"SELECT id FROM {table} WHERE description = ?", [description])
        return cur.fetchone()[0]
    except TypeError:
        logger.log(f"[ERROR] {description} not found in {table} table")
        return None


def main():
    console = Console()
    log = Console(file=open(LOG_FILE, "w", encoding="utf-8"))

    file_arg, quiet = get_args()

    try:
        folder_id = Folder.get_by_name("Digitalizzazioni Tommasoli").id
    except:
        if not quiet:
            console.print(f"[red]Error looking for folder_id[/red]")
        exit(69)

    for row in track(Importer(file_arg, MAPPING).next_row(), description="[cyan]Praying it works :pray:..."):
        row["folder_id"] = folder_id
        row["published"] = safe_replace(row["published"], {"si": 1, "no": 0})
        row["is_horizontal"] = safe_replace(row["is_horizontal"], {"orizzontale": 1, "verticale": 0})
        row["is_original"] = safe_replace(row["is_original"], {"si": 1, "no": 0})
        row["mtx_id"] = safe_replace(row["mtx_id"], {"bn": "b/n"})

        date_from = create_date(row.pop("year_from"), row.pop("month_from"), row.pop("day_from"))
        date_to = create_date(row.pop("year_to"))

        row["dts_from_dates_id"] = None if date_from is None else date_from.id
        row["dts_to_dates_id"] = None if date_to is None else date_to.id

        # should create a items_has_place row instead
        place_id = row.pop("place_id")

        row["mtx_id"] = get_id_from_description(row["mtx_id"], "mtx", log)
        row["medium_id"] = get_id_from_description(row["medium_id"], "medium", log)
        row["stcc_d_id"] = get_id_from_description(row["stcc_d_id"], "stcc_d", log) 
        row["ogtd_id"] = get_id_from_description(row["ogtd_id"], "ogt_d", log)

        item = Item(**row)
        try:
            item.save()
        except mariadb.IntegrityError:
            log.log(f"[ERROR] saving item_place for item {item.id} - {item.signature} signature is duplicated but should be unique")
            if not quiet:
                console.log(f"[red]ERROR[/red] :boom: saving item_place for item {item.id} - {item.signature} signature is duplicated but should be unique")
            continue
        item_place = ItemHasPlace(
            item_id=item.id,
            place_id=place_id,
        )
        item_place.save()

        item.item_has_place_id = item_place.id
        item.update()

        proprietario_bene = AutpeHasItem(
            autpe_id=row["Proprietario del bene"],
            item_id=item.id,
            item_column="cdgs",
            autr_id=None
        )
        proprietario_bene.save()

        if row.get("responsability") is not None:
            responsability = AutpeHasItem(
                autpe_id=row["responsability"],
                item_id=item.id,
                item_column="responsability",
                autr_id=30
            )
            responsability.save()

        with open("config.json") as f:
            config = json.load(f)
        source_path = f"{config['foto_dir']['source']}/{item.sgtt}.jpg"
        output_path = config["foto_dir"]["output"]

        if not os.path.exists(source_path):
            source_path = f"{config['foto_dir']['source']}/{item.sgtt}.JPG"

        try:
            shutil.copy(source_path, output_path)
            Attachment(
                item_id=item.id,
                # nome del file con estensione
                filename=source_path.split("/")[-1],
                original_url=f"import_tommasoli/{source_path.split('/')[-1]}"
            ).save()
        except FileNotFoundError:
            #log.log(f"[ERROR] Entry {item.sgtt} non ha un file corrispondente con lo stesso nome")
            Attachment(
                item_id=item.id,
                filename=source_path.split("/")[-1],
                original_url=f"import_tommasoli/{source_path.split('/')[-1]}"
            ).save()
        
        try:
            LogForm(record_id=item.id).save() # type: ignore
        except Exception as e:
            console.log(f"[red]ERROR[/red] :boom: saving log form for item {item.id}")
            console.log(e)


    if not quiet:
        table = Table(title="Items")
        table.add_column("id", justify="right", style="cyan", no_wrap=True)
        table.add_column("title", style="magenta")
        table.add_column("title integr", style="magenta")
        table.add_column("published", style="green")
        table.add_column("places id", style="cyan")
        table.add_column("ogtd", style="magenta")
        for item in Item.get_all():
            table.add_row(
                str(item.id),
                item.sgtt,
                item.sgtt_ext,
                str(item.published),
                ",".join([elem.place_id for elem in ItemHasPlace.get_by_item_id(item.id) if elem.place_id is not None]), # type: ignore
                str(OgtD.get_by_id(item.ogtd_id).description if item.ogtd_id is not None else None)
            )

        console.print(table)

    photo_diff = verify_photo_number()
    log.log(f"[INFO] {len(photo_diff)} non sono state importate perché non hanno una entry corrispondente nel file excel")
    if not quiet:
        console.log(f"{len(photo_diff)} non sono state importate perché non hanno una entry corrispondente nel file excel")
    for elem in photo_diff:
        log.log(f"[INFO]         File {elem} non trovato nel file excel")


    prompt = Prompt.ask("Do you want to save the session to db? [y/n]", choices=["y", "n"], default="n")

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
