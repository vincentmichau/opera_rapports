from __future__ import annotations

import json
import sqlite3
from collections.abc import Iterable
from datetime import date
from pathlib import Path

from platformdirs import user_data_dir

from opera_rapports.core.models import Gender, Guest, Language

APP_NAME = "OperaRapports"

SCHEMA = """
PRAGMA journal_mode=WAL;
CREATE TABLE IF NOT EXISTS guests (
  reservation_id TEXT PRIMARY KEY,
  full_name TEXT NOT NULL,
  last_name TEXT NOT NULL,
  first_name TEXT NOT NULL,
  title_raw TEXT,
  gender TEXT NOT NULL,
  language TEXT NOT NULL,
  arrival_date TEXT,
  departure_date TEXT,
  room_number TEXT,
  room_type TEXT,
  adults INTEGER NOT NULL DEFAULT 1,
  children INTEGER NOT NULL DEFAULT 0,
  raw_json TEXT NOT NULL DEFAULT '{}',
  imported_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS settings (
  key TEXT PRIMARY KEY,
  value_json TEXT NOT NULL
);
"""


def default_db_path() -> Path:
    root = Path(user_data_dir(APP_NAME, appauthor=False))
    root.mkdir(parents=True, exist_ok=True)
    return root / "opera_rapports.sqlite3"


def _date_to_text(value: date | None) -> str | None:
    return value.isoformat() if value else None


def _date_from_text(value: str | None) -> date | None:
    return date.fromisoformat(value) if value else None


class Repository:
    def __init__(self, path: str | Path | None = None) -> None:
        self.path = Path(path) if path else default_db_path()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(self.path)
        self.connection.row_factory = sqlite3.Row
        self.connection.executescript(SCHEMA)

    def close(self) -> None:
        self.connection.close()

    def replace_import(self, guests: Iterable[Guest]) -> int:
        rows = list(guests)
        with self.connection:
            self.connection.execute("DELETE FROM guests")
            self.connection.executemany(
                """
                INSERT INTO guests (
                  reservation_id, full_name, last_name, first_name, title_raw, gender, language,
                  arrival_date, departure_date, room_number, room_type, adults, children, raw_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        guest.reservation_id,
                        guest.full_name,
                        guest.last_name,
                        guest.first_name,
                        guest.title_raw,
                        guest.gender.value,
                        guest.language.value,
                        _date_to_text(guest.arrival_date),
                        _date_to_text(guest.departure_date),
                        guest.room_number,
                        guest.room_type,
                        guest.adults,
                        guest.children,
                        json.dumps(guest.raw, ensure_ascii=False),
                    )
                    for guest in rows
                ],
            )
        return len(rows)

    def list_guests(self, arrival: date | None = None) -> list[Guest]:
        query = "SELECT * FROM guests"
        params: list[str] = []
        if arrival:
            query += " WHERE arrival_date = ?"
            params.append(arrival.isoformat())
        query += " ORDER BY arrival_date, room_number, last_name"
        return [self._row_to_guest(row) for row in self.connection.execute(query, params)]

    def update_guest_language_gender(self, reservation_id: str, language: Language, gender: Gender) -> None:
        with self.connection:
            self.connection.execute(
                "UPDATE guests SET language = ?, gender = ? WHERE reservation_id = ?",
                (language.value, gender.value, reservation_id),
            )

    def clear_guests(self) -> None:
        with self.connection:
            self.connection.execute("DELETE FROM guests")

    def get_setting(self, key: str, default: object = None) -> object:
        row = self.connection.execute("SELECT value_json FROM settings WHERE key = ?", (key,)).fetchone()
        return json.loads(row["value_json"]) if row else default

    def set_setting(self, key: str, value: object) -> None:
        with self.connection:
            self.connection.execute(
                "INSERT INTO settings(key, value_json) VALUES(?, ?) ON CONFLICT(key) DO UPDATE SET value_json = excluded.value_json",
                (key, json.dumps(value, ensure_ascii=False)),
            )

    @staticmethod
    def _row_to_guest(row: sqlite3.Row) -> Guest:
        return Guest(
            reservation_id=row["reservation_id"],
            full_name=row["full_name"],
            last_name=row["last_name"],
            first_name=row["first_name"],
            title_raw=row["title_raw"] or "",
            gender=Gender(row["gender"]),
            language=Language(row["language"]),
            arrival_date=_date_from_text(row["arrival_date"]),
            departure_date=_date_from_text(row["departure_date"]),
            room_number=row["room_number"] or "",
            room_type=row["room_type"] or "",
            adults=row["adults"],
            children=row["children"],
            raw=json.loads(row["raw_json"] or "{}"),
        )
