from pathlib import Path

import duckdb

from app.core.config import settings


def _quote_identifier(name: str) -> str:
    """Escape a SQL identifier to prevent injection in double-quoted contexts."""
    return '"' + name.replace('"', '""') + '"'


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
        quoted = _quote_identifier(table_name)
        schema = self.conn.execute(f"DESCRIBE {quoted}").fetchall()
        row_count = self.conn.execute(f"SELECT COUNT(*) FROM {quoted}").fetchone()[0]
        self.tables[table_name] = {
            "schema": schema,
            "row_count": row_count,
        }

    def ingest_csv(self, file_path: str, table_name: str) -> None:
        quoted = _quote_identifier(table_name)
        self.conn.execute(
            f"CREATE OR REPLACE TABLE {quoted} AS SELECT * FROM read_csv_auto(?)",
            [file_path],
        )
        self._cache_table_metadata(table_name)

    def drop_table(self, table_name: str) -> None:
        self.conn.execute(f"DROP TABLE IF EXISTS {_quote_identifier(table_name)}")
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
