import re
from pathlib import Path

import duckdb

from app.core.config import settings

_SAFE_TABLE_NAME = re.compile(r"[^a-zA-Z0-9_]")


def _sanitize_table_name(name: str) -> str:
    """Strip unsafe characters from a table name to prevent SQL injection."""
    return _SAFE_TABLE_NAME.sub("_", name)


class StructuredStore:
    def __init__(self) -> None:
        db_path = Path(settings.data_dir) / "structured.duckdb"
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = duckdb.connect(str(db_path))
        self.tables: dict[str, dict] = {}
        self._load_existing_tables()

    def _load_existing_tables(self) -> None:
        rows = self.conn.execute("SHOW TABLES").fetchall()
        for (table_name,) in rows:
            self._cache_table_metadata(table_name)

    def _cache_table_metadata(self, table_name: str) -> None:
        schema = self.conn.execute(f'DESCRIBE "{table_name}"').fetchall()
        row_count = self.conn.execute(
            f'SELECT COUNT(*) FROM "{table_name}"'
        ).fetchone()[0]
        self.tables[table_name] = {
            "schema": schema,
            "row_count": row_count,
        }

    def ingest_csv(self, file_path: str, table_name: str) -> str:
        """Ingest a CSV file as a DuckDB table. Returns the sanitized name."""
        safe_name = _sanitize_table_name(table_name)
        self.conn.execute(
            f'CREATE OR REPLACE TABLE "{safe_name}" AS SELECT * FROM read_csv_auto(?)',
            [file_path],
        )
        self._cache_table_metadata(safe_name)
        return safe_name

    def drop_table(self, table_name: str) -> None:
        self.conn.execute(f'DROP TABLE IF EXISTS "{table_name}"')
        self.tables.pop(table_name, None)

    def execute_query(self, query: str) -> str:
        try:
            result = self.conn.execute(query).fetchall()
            if not result:
                return "Query returned no results."
            columns = [desc[0] for desc in self.conn.description]
            header = " | ".join(columns)
            separator = " | ".join("---" for _ in columns)
            rows = [" | ".join(str(v) for v in row) for row in result]
            return f"{header}\n{separator}\n" + "\n".join(rows)
        except duckdb.Error as e:
            return f"SQL Error: {e}. Please check the query and try again."

    def has_data(self) -> bool:
        return len(self.tables) > 0

    def get_schema_summary(self) -> str:
        if not self.tables:
            return "No structured data available."

        parts = []
        for table_name, info in self.tables.items():
            cols = ", ".join(f"{col[0]} ({col[1]})" for col in info["schema"])
            parts.append(
                f'Table "{table_name}" ({info["row_count"]} rows): columns [{cols}]'
            )
        return "\n".join(parts)

    def table_exists(self, table_name: str) -> bool:
        return table_name in self.tables
