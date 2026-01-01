from __future__ import annotations

import os
import json
import sqlite3
import tempfile

from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv
import socket


load_dotenv()

scripts_dir = Path("db/sql")
fallback_path = Path("db/fallback_records.json")


def new_db_conn():
    db_path = os.getenv('DB_PATH', None)
    if not db_path:
        raise ValueError("env var 'DB_PATH' not found.")
    try:
        conn = sqlite3.connect(Path(db_path))
    except Exception as e:
        err_msg = f"Unable to connect to database {Path(db_path).stem}: {e}"
        raise Exception(err_msg)

    return conn


def init_db(conn: sqlite3.Connection):

    script_path = scripts_dir / "db_init.sql"
    if not script_path.exists():
        raise FileNotFoundError(
            f"Sql script '{script_path.name}' does not exist in directory '{scripts_dir.absolute()}'")

    try:
        conn.executescript(str(script_path))
    except Exception as e:
        raise Exception(
            f"Failed to initialize database: {e}"
        )
    conn.commit()


def prune_db(conn: sqlite3.Connection):
    script_path = scripts_dir / "prune.sql"
    if not script_path.exists():
        raise FileNotFoundError(
            f"Sql script '{script_path.name}' does not exist in directory '{scripts_dir.absolute()}'")

    sql_text = script_path.read_text()
    if not sql_text or sql_text == "":
        raise ValueError(
            f"SQL script '{str(script_path)}' is empty."
        )

    max_records = int(os.getenv("MAX_RECORDS", "300"))

    device_name = socket.gethostname()

    script_params = (device_name, device_name, max_records,)

    try:
        conn.execute(
            sql_text,
            script_params
        )
    except Exception as e:
        raise Exception(
            f"Failed to prune database: {e}"
        )

    conn.commit()


@dataclass
class NetworkRecord:

    device_name: str
    timestamp: float
    adapter: str
    down_mbps: float
    up_mbps: float
    rx_bytes: int
    tx_bytes: int


def save_fallback_records(records: list[NetworkRecord], json_path: Path = fallback_path, overwrite: bool = False):
    fallback_content = []
    if json_path.exists() and overwrite:
        os.remove(str(json_path))
    elif json_path.exists() and not overwrite:
        current_content = json.loads(json_path.read_text())
        if len(current_content) > 0:
            fallback_content.extend(current_content)
    fallback_content.extend(records)

    fallback_json = []
    for record in fallback_content:
        if not isinstance(record, NetworkRecord):
            fallback_json.append(
                NetworkRecord(*record).__dict__
            )
        else:
            fallback_json.append(
                record.__dict__
            )

    with tempfile.TemporaryFile(mode='w+t') as tf:
        try:
            json.dump(fallback_json, tf, indent=4)
        except Exception as e:
            raise Exception(
                f"Fallback records failed to save: {e}"
            )
        tf.seek(0)
        os.remove(str(json_path))
        json_path.write_text(tf.read())


def push_fallback_records(conn: sqlite3.Connection, json_path: Path):
    if (not json_path.exists()) or (not json_path.read_text().strip()):
        return
    fallback = json.loads(json_path.read_text(encoding='utf8'))
    records = [NetworkRecord(*r) for r in fallback]
    insert_records(conn, records)


def insert_records(conn: sqlite3.Connection, records: list[NetworkRecord]) -> None:
    script_path = scripts_dir / "insert_net_record.sql"
    if not script_path.exists():
        raise FileNotFoundError(
            f"Sql script '{script_path.name}' does not exist in directory '{scripts_dir.absolute()}'")

    sql_text = script_path.read_text()
    if not sql_text or sql_text == "":
        raise ValueError(
            f"SQL script '{str(script_path)}' is empty."
        )
    try:
        conn.executemany(
            sql_text,
            (records,)
        )
        conn.commit()
    except Exception as e:
        save_fallback_records(records=records)
