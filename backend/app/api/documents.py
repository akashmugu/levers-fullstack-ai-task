import shutil
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, Request, UploadFile

from app.core.config import settings
from app.models.schemas import IngestResponse
from app.utils.chunking import chunk_markdown

router = APIRouter()

SUPPORTED_EXTENSIONS = {".md", ".csv", ".txt"}


@router.post("/api/documents", response_model=IngestResponse)
async def upload_document(request: Request, file: UploadFile = File(...)):
    ext = Path(file.filename).suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {ext}. Supported: {sorted(SUPPORTED_EXTENSIONS)}",
        )

    upload_dir = Path(settings.data_dir) / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_path = upload_dir / file.filename

    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    if ext == ".csv":
        store = request.app.state.structured_store
        store.ingest_csv(str(file_path), file.filename)
        return IngestResponse(
            filename=file.filename,
            doc_type="structured",
            detail=f"Loaded as table '{file.filename}'",
        )

    content = file_path.read_text()
    chunks = chunk_markdown(content, source=file.filename)
    store = request.app.state.vector_store

    if store.document_exists(file.filename):
        store.delete_document(file.filename)

    store.add_chunks(chunks)
    return IngestResponse(
        filename=file.filename,
        doc_type="unstructured",
        detail=f"Created {len(chunks)} chunks",
    )


@router.get("/api/documents")
async def list_documents(request: Request):
    vector_store = request.app.state.vector_store
    structured_store = request.app.state.structured_store

    unstructured: list[str] = []
    if vector_store.has_documents():
        all_meta = vector_store.collection.get()["metadatas"]
        unstructured = sorted({m.get("source", "unknown") for m in all_meta})

    structured = list(structured_store.tables.keys()) if structured_store.has_data() else []

    return {"unstructured": unstructured, "structured": structured}


@router.delete("/api/documents/{filename}")
async def delete_document(filename: str, request: Request):
    vector_store = request.app.state.vector_store
    structured_store = request.app.state.structured_store
    deleted = False

    if vector_store.document_exists(filename):
        vector_store.delete_document(filename)
        deleted = True

    if structured_store.table_exists(filename):
        structured_store.drop_table(filename)
        deleted = True

    upload_path = Path(settings.data_dir) / "uploads" / filename
    if upload_path.exists():
        upload_path.unlink()

    if not deleted:
        raise HTTPException(
            status_code=404, detail=f"Document '{filename}' not found"
        )

    return {"detail": f"Document '{filename}' deleted"}
