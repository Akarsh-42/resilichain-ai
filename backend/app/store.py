import sqlite3
from pathlib import Path

from .models import ScenarioState


class StateStore:
    def __init__(self, database_path: str | Path = "resilichain.db") -> None:
        self.database_path = str(database_path)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.database_path)

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS scenario_state (
                    scenario_id TEXT PRIMARY KEY,
                    payload TEXT NOT NULL
                )
                """
            )

    def save(self, state: ScenarioState) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO scenario_state (scenario_id, payload)
                VALUES (?, ?)
                ON CONFLICT(scenario_id) DO UPDATE SET payload = excluded.payload
                """,
                (state.scenario_id, state.model_dump_json()),
            )

    def get(self, scenario_id: str) -> ScenarioState | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT payload FROM scenario_state WHERE scenario_id = ?",
                (scenario_id,),
            ).fetchone()
        return ScenarioState.model_validate_json(row[0]) if row else None

