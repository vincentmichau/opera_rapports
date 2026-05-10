from __future__ import annotations

import json
import sqlite3
from collections.abc import Iterable
from datetime import date
from pathlib import Path
from opera_rapports.core.audit import AuditEvent
from opera_rapports.core.models import Gender, Guest, Language

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
CREATE TABLE IF NOT EXISTS audit_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  action TEXT NOT NULL,
  details TEXT NOT NULL DEFAULT '',
  created_at TEXT NOT NULL
);
"""


def date_to_text(value: date | None) -> str | None:
    return value.isoformat() if value else None


def date_from_text(value: str | None) -> date | None:
    return date.fromisoformat(value) if value else None


class GuestDAO:
    """Data Access Object dedicated to arrival/guest persistence."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def replace_all(self, guests: Iterable[Guest]) -> int:
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
                [self._guest_to_tuple(guest) for guest in rows],
            )
        return len(rows)

    def list(self, arrival: date | None = None) -> list[Guest]:
        query = "SELECT * FROM guests"
        params: list[str] = []
        if arrival:
            query += " WHERE arrival_date = ?"
            params.append(arrival.isoformat())
        query += " ORDER BY arrival_date, room_number, last_name"
        return [self._row_to_guest(row) for row in self.connection.execute(query, params)]

    def update_language_gender(self, reservation_id: str, language: Language, gender: Gender) -> None:
        with self.connection:
            self.connection.execute(
                "UPDATE guests SET language = ?, gender = ? WHERE reservation_id = ?",
                (language.value, gender.value, reservation_id),
            )

    def clear(self) -> None:
        with self.connection:
            self.connection.execute("DELETE FROM guests")

    def purge_older_than(self, days: int) -> int:
        with self.connection:
            cursor = self.connection.execute(
                "DELETE FROM guests WHERE imported_at < datetime('now', ?)",
                (f"-{max(int(days), 1)} days",),
            )
        return cursor.rowcount

    @staticmethod
    def _guest_to_tuple(guest: Guest) -> tuple[object, ...]:
        return (
            guest.reservation_id,
            guest.full_name,
            guest.last_name,
            guest.first_name,
            guest.title_raw,
            guest.gender.value,
            guest.language.value,
            date_to_text(guest.arrival_date),
            date_to_text(guest.departure_date),
            guest.room_number,
            guest.room_type,
            guest.adults,
            guest.children,
            json.dumps(guest.raw, ensure_ascii=False),
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
            arrival_date=date_from_text(row["arrival_date"]),
            departure_date=date_from_text(row["departure_date"]),
            room_number=row["room_number"] or "",
            room_type=row["room_type"] or "",
            adults=row["adults"],
            children=row["children"],
            raw=json.loads(row["raw_json"] or "{}"),
        )


class SettingsDAO:
    """Data Access Object dedicated to generic JSON application settings."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def get(self, key: str, default: object = None) -> object:
        row = self.connection.execute("SELECT value_json FROM settings WHERE key = ?", (key,)).fetchone()
        return json.loads(row["value_json"]) if row else default

    def set(self, key: str, value: object) -> None:
        with self.connection:
            self.connection.execute(
                "INSERT INTO settings(key, value_json) VALUES(?, ?) ON CONFLICT(key) DO UPDATE SET value_json = excluded.value_json",
                (key, json.dumps(value, ensure_ascii=False)),
            )


class AuditDAO:
    """DAO for local non-sensitive audit events."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def record(self, event: AuditEvent) -> None:
        with self.connection:
            self.connection.execute(
                "INSERT INTO audit_log(action, details, created_at) VALUES(?, ?, ?)",
                (event.action, event.details, event.created_at),
            )

    def list_recent(self, limit: int = 50) -> list[AuditEvent]:
        rows = self.connection.execute(
            "SELECT action, details, created_at FROM audit_log ORDER BY id DESC LIMIT ?",
            (max(int(limit), 1),),
        ).fetchall()
        return [AuditEvent(action=row["action"], details=row["details"], created_at=row["created_at"]) for row in rows]

    def purge_older_than(self, days: int) -> int:
        with self.connection:
            cursor = self.connection.execute(
                "DELETE FROM audit_log WHERE created_at < datetime('now', ?)",
                (f"-{max(int(days), 1)} days",),
            )
        return cursor.rowcount


class DAOFactory:
    """Factory centralising SQLite connection creation and DAO construction."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(self.path)
        self.connection.row_factory = sqlite3.Row
        self.connection.executescript(SCHEMA)
        self._guest_dao: GuestDAO | None = None
        self._settings_dao: SettingsDAO | None = None
        self._audit_dao: AuditDAO | None = None

    @property
    def guests(self) -> GuestDAO:
        if self._guest_dao is None:
            self._guest_dao = GuestDAO(self.connection)
        return self._guest_dao

    @property
    def settings(self) -> SettingsDAO:
        if self._settings_dao is None:
            self._settings_dao = SettingsDAO(self.connection)
        return self._settings_dao

    @property
    def audit(self) -> AuditDAO:
        if self._audit_dao is None:
            self._audit_dao = AuditDAO(self.connection)
        return self._audit_dao

    def close(self) -> None:
        self.connection.close()
