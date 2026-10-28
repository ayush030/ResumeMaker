import hashlib
import json
import sqlite3

from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from src.schemas.candidate import CandidateProfile


DEFAULT_DB_PATH = Path("data/profiles.db")


class ProfileRepository:
    def __init__(self, db_path: Path = DEFAULT_DB_PATH):
        self.db_path = Path(db_path)

    def initialize(self) -> None:
        """Create the database and required table."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        with sqlite3.connect(self.db_path) as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS candidate_profiles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    candidate_id TEXT NOT NULL,
                    source_sha256 TEXT NOT NULL,
                    schema_version INTEGER NOT NULL,
                    profile_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,

                    UNIQUE (
                        candidate_id,
                        source_sha256,
                        schema_version
                    )
                )
                """
            )

    @staticmethod
    def calculate_file_hash(file_path: Path) -> str:
        """Return the SHA-256 hash of a resume file."""
        sha256 = hashlib.sha256()

        with Path(file_path).open("rb") as file:
            for chunk in iter(lambda: file.read(8192), b""):
                sha256.update(chunk)

        return sha256.hexdigest()

    def get_profile(
        self,
        candidate_id: str,
        source_sha256: str,
        schema_version: int = 1,
    ) -> Optional[CandidateProfile]:
        """Return the cached profile, or None if no match exists."""
        with sqlite3.connect(self.db_path) as connection:
            connection.row_factory = sqlite3.Row

            row = connection.execute(
                """
                SELECT profile_json
                FROM candidate_profiles
                WHERE candidate_id = ?
                  AND source_sha256 = ?
                  AND schema_version = ?
                """,
                (candidate_id, source_sha256, schema_version),
            ).fetchone()

        if row is None:
            return None

        return CandidateProfile.model_validate_json(
            row["profile_json"]
        )

    def save_profile(
        self,
        candidate_id: str,
        source_sha256: str,
        profile: CandidateProfile,
    ) -> None:
        """Insert or update the profile for this source version."""
        now = datetime.now(timezone.utc).isoformat()
        profile_json = profile.model_dump_json()

        with sqlite3.connect(self.db_path) as connection:
            connection.execute(
                """
                INSERT INTO candidate_profiles (
                    candidate_id,
                    source_sha256,
                    schema_version,
                    profile_json,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?)

                ON CONFLICT (
                    candidate_id,
                    source_sha256,
                    schema_version
                )
                DO UPDATE SET
                    profile_json = excluded.profile_json,
                    updated_at = excluded.updated_at
                """,
                (
                    candidate_id,
                    source_sha256,
                    profile.schema_version,
                    profile_json,
                    now,
                    now,
                ),
            )
