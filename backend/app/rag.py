import os
from pypdf import PdfReader

def load_document(file_path: str) -> str:
    """
    Loads text content from a file. Supports .txt, .md, and .pdf.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    ext = os.path.splitext(file_path)[1].lower()
    if ext in (".txt", ".md"):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    elif ext == ".pdf":
        reader = PdfReader(file_path)
        text_parts = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                text_parts.append(text)
        return "\n".join(text_parts)
    else:
        raise ValueError(f"Unsupported file format: {ext}")


class RecursiveCharacterTextSplitter:
    """
    Splits text recursively using a hierarchy of separators to keep chunks
    within a target size and overlap.
    """
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200, separators: list[str] = None):
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size")
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators or ["\n\n", "\n", " ", ""]

    def split_text(self, text: str) -> list[str]:
        return self._split_text(text, self.separators)

    def _split_text(self, text: str, separators: list[str]) -> list[str]:
        if len(text) <= self.chunk_size:
            return [text]

        # Find the first separator that exists in the text
        separator = ""
        remaining_separators = []
        for i, sep in enumerate(separators):
            if sep == "":
                separator = sep
                remaining_separators = separators[i+1:]
                break
            if sep in text:
                separator = sep
                remaining_separators = separators[i+1:]
                break

        # Split the text
        if separator != "":
            splits = text.split(separator)
        else:
            splits = list(text)

        # Recursively split any chunk that is too large
        final_splits = []
        for split in splits:
            if len(split) > self.chunk_size:
                if not remaining_separators:
                    # No more separators, split by characters
                    start = 0
                    while start < len(split):
                        final_splits.append(split[start:start + self.chunk_size])
                        start += self.chunk_size
                else:
                    final_splits.extend(self._split_text(split, remaining_separators))
            else:
                final_splits.append(split)

        # Merge splits into chunks under self.chunk_size with overlap
        chunks = []
        current_chunk = []
        current_length = 0

        for split in final_splits:
            split_len = len(split)
            added_len = split_len + (len(separator) if current_chunk and separator else 0)

            if current_length + added_len <= self.chunk_size:
                current_chunk.append(split)
                current_length += added_len
            else:
                if current_chunk:
                    chunks.append(separator.join(current_chunk))
                
                # Keep items from the end of current_chunk to respect overlap
                while current_chunk:
                    current_chunk.pop(0)
                    new_len = sum(len(x) for x in current_chunk) + (len(separator) * (len(current_chunk) - 1) if len(current_chunk) > 1 else 0)
                    new_added_len = split_len + (len(separator) if current_chunk and separator else 0)
                    if new_len + new_added_len <= self.chunk_size and new_len <= self.chunk_overlap:
                        current_length = new_len + new_added_len
                        current_chunk.append(split)
                        break
                else:
                    current_chunk = [split]
                    current_length = split_len

        if current_chunk:
            chunks.append(separator.join(current_chunk))

        return chunks


from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models import DocumentChunk

def store_document_chunks(db: Session, document_id: int, chunks: list[str], embeddings: list[list[float]]) -> None:
    """
    Store document chunks with their vector embeddings in PostgreSQL.
    """
    for chunk, embedding in zip(chunks, embeddings):
        db_chunk = DocumentChunk(
            document_id=document_id,
            content=chunk,
            embedding=embedding
        )
        db.add(db_chunk)
    db.commit()

def query_similar_chunks(db: Session, query_embedding: list[float], limit: int = 5) -> list[DocumentChunk]:
    """
    Retrieve document chunks ordered by similarity (distance) to the query embedding.
    """
    stmt = (
        select(DocumentChunk)
        .order_by(DocumentChunk.embedding.cosine_distance(query_embedding))
        .limit(limit)
    )
    return list(db.scalars(stmt).all())

