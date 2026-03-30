import csv
from pathlib import Path

import pytest

from app.services.structured_store import StructuredStore
from app.services.vector_store import VectorStore


class TestVectorStore:
    @pytest.fixture()
    def store(self, tmp_data_dir: Path) -> VectorStore:
        return VectorStore()

    def test_empty_store_has_no_documents(self, store: VectorStore) -> None:
        assert store.has_documents() is False

    def test_add_and_search(self, store: VectorStore) -> None:
        chunks = [
            {
                "id": "1",
                "text": "FDCPA prohibits calling before 8 AM",
                "metadata": {"source": "fdcpa.md", "section": "Calling Hours"},
            },
            {
                "id": "2",
                "text": "Always give the Mini-Miranda disclosure",
                "metadata": {"source": "fdcpa.md", "section": "Disclosures"},
            },
        ]
        store.add_chunks(chunks)
        assert store.has_documents() is True

        results = store.search("calling hours")
        assert len(results) > 0
        assert results[0]["metadata"]["source"] == "fdcpa.md"

    def test_delete_document(self, store: VectorStore) -> None:
        store.add_chunks(
            [
                {
                    "id": "1",
                    "text": "Some content",
                    "metadata": {"source": "to_delete.md", "section": ""},
                },
            ]
        )
        assert store.document_exists("to_delete.md") is True
        store.delete_document("to_delete.md")
        assert store.document_exists("to_delete.md") is False

    def test_search_empty_store(self, store: VectorStore) -> None:
        results = store.search("anything")
        assert results == []

    def test_get_document_summary(self, store: VectorStore) -> None:
        store.add_chunks(
            [
                {
                    "id": "1",
                    "text": "content",
                    "metadata": {"source": "doc_a.md", "section": ""},
                },
                {
                    "id": "2",
                    "text": "content",
                    "metadata": {"source": "doc_b.md", "section": ""},
                },
            ]
        )
        summary = store.get_document_summary()
        assert "doc_a.md" in summary
        assert "doc_b.md" in summary


class TestStructuredStore:
    @pytest.fixture()
    def store(self, tmp_data_dir: Path) -> StructuredStore:
        return StructuredStore()

    @pytest.fixture()
    def sample_csv(self, tmp_data_dir: Path) -> Path:
        csv_path = tmp_data_dir / "accounts.csv"
        with open(csv_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["account_id", "name", "status"])
            writer.writerow(["ACC-001", "John Doe", "active"])
            writer.writerow(["ACC-002", "Jane Smith", "disputed"])
        return csv_path

    def test_empty_store(self, store: StructuredStore) -> None:
        assert store.has_data() is False

    def test_ingest_and_query(self, store: StructuredStore, sample_csv: Path) -> None:
        store.ingest_csv(str(sample_csv), "accounts")
        assert store.has_data() is True
        assert store.table_exists("accounts") is True

        result = store.execute_query(
            "SELECT * FROM accounts WHERE account_id = 'ACC-001'"
        )
        assert "John Doe" in result

    def test_schema_summary(self, store: StructuredStore, sample_csv: Path) -> None:
        store.ingest_csv(str(sample_csv), "accounts")
        summary = store.get_schema_summary()
        assert "accounts" in summary
        assert "2 rows" in summary

    def test_drop_table(self, store: StructuredStore, sample_csv: Path) -> None:
        store.ingest_csv(str(sample_csv), "accounts")
        store.drop_table("accounts")
        assert store.table_exists("accounts") is False

    def test_bad_sql_returns_error(self, store: StructuredStore) -> None:
        result = store.execute_query("SELECT * FROM nonexistent_table")
        assert "SQL Error" in result
