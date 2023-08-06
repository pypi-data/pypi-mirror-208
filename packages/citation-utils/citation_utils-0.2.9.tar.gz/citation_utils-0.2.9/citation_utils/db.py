import sys
from pathlib import Path
from sqlite3 import IntegrityError

import yaml
from loguru import logger
from sqlite_utils.db import Database

from .main import Citation

BASE = Path().home().joinpath("code/corpus/decisions")
DECISIONS = BASE.glob("**/*/details.yaml")
ERR = ["orig_idx", "docket", "date_prom"]

logger.configure(
    handlers=[
        {
            "sink": sys.stdout,
            "format": "{message}",
            "level": "ERROR",
        },
        {
            "sink": "logs/citations.log",
            "format": "{message}",
            "level": "DEBUG",
            "serialize": True,
        },
        {
            "sink": "logs/citation_errors.log",
            "format": "{message}",
            "level": "ERROR",
            "serialize": True,
        },
    ]
)


def set_row(detail: Path) -> dict:
    """All details.yaml should have a docket, if they don't then likely error."""
    base = dict(path=detail.parent.parent.stem, origin=detail.parent.stem)
    data = yaml.safe_load(detail.read_bytes())
    obj = Citation.extract_citation_from_data(data)
    if obj.docket and obj.slug:
        res = {"valid": True, "title": data.get("case_title"), "id": obj.slug}
        return base | res | obj.dict()
    else:
        err = {k: v for k, v in data.items() if k in ERR}
        return base | {"valid": False} | err


def setup_db():
    """Create a helper database to examine contents of local folder when parsed
    as a Citation object."""
    db = Database("raw.db", use_counts_table=True, recreate=True)
    for detail in DECISIONS:
        if row := set_row(detail):
            if row["valid"] is True:
                try:
                    db["valid"].insert(row, pk="id", column_order="id")  # type: ignore
                except IntegrityError:
                    p = BASE.joinpath(f"{row['path']}/{row['origin']}")
                    logger.error(f"Duplicate: {row['id']=} {p=}")
            else:
                db["invalid"].insert(row)  # type: ignore
    els = ["docket_category", "docket_serial", "docket_date"]
    db["valid"].create_index(els)  # type: ignore
    db["valid"].create_index(["docket_category", "docket_serial"])  # type: ignore
    db["valid"].create_index(["docket_category"])  # type: ignore
    db["valid"].create_index(["docket_serial"])  # type: ignore
    db["valid"].create_index(["docket_date"])  # type: ignore
    db["valid"].create_index(["docket"])  # type: ignore
    db["valid"].create_index(["phil"])  # type: ignore
    db["valid"].create_index(["scra"])  # type: ignore
