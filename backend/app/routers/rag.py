"""RAG document upload endpoint."""

import tempfile
from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.rag import load_document, RecursiveCharacterTextSplitter
from app.embeddings import EmbeddingGenerator
from app.models import Document


router = APIRouter()


@router.post("/rag/upload")
async def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Accept a file upload (.txt, .md, .pdf), chunk it, embed it, and store in the DB."""
    # Save uploaded file to temp location
    with tempfile.NamedTemporaryFile(delete=False, suffix=file.filename) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    # Load document text
    text = load_document(tmp_path)

    # Split into chunks
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_text(text)

    # Generate embeddings
    generator = EmbeddingGenerator()
    embeddings = generator.generate_embeddings(chunks)

    # Create Document record
    document = Document(title=file.filename, content=text)
    db.add(document)
    db.commit()
    db.refresh(document)

    # Store chunks with embeddings
    from app.rag import store_document_chunks

    store_document_chunks(db, document.id, chunks, embeddings)

    return {"document_id": document.id, "chunk_count": len(chunks)}
