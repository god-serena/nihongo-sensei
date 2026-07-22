import os
import pytest
from unittest.mock import MagicMock, patch
from app.rag import load_document, RecursiveCharacterTextSplitter

def test_load_document_text_and_md(tmp_path):
    # Test TXT
    txt_file = tmp_path / "test.txt"
    txt_content = "Hello World!\nThis is a test."
    txt_file.write_text(txt_content, encoding="utf-8")
    
    assert load_document(str(txt_file)) == txt_content

    # Test MD
    md_file = tmp_path / "test.md"
    md_content = "# Title\n- Item 1\n- Item 2"
    md_file.write_text(md_content, encoding="utf-8")
    
    assert load_document(str(md_file)) == md_content

def test_load_document_pdf(tmp_path):
    pdf_file = tmp_path / "test.pdf"
    pdf_file.touch()

    # Mock PdfReader and pages
    mock_page_1 = MagicMock()
    mock_page_1.extract_text.return_value = "Page 1 Content"
    mock_page_2 = MagicMock()
    mock_page_2.extract_text.return_value = "Page 2 Content"

    with patch("app.rag.PdfReader") as mock_pdf_reader:
        mock_reader_instance = MagicMock()
        mock_reader_instance.pages = [mock_page_1, mock_page_2]
        mock_pdf_reader.return_value = mock_reader_instance

        content = load_document(str(pdf_file))
        assert content == "Page 1 Content\nPage 2 Content"
        mock_pdf_reader.assert_called_once_with(str(pdf_file))

def test_load_document_invalid_format(tmp_path):
    invalid_file = tmp_path / "test.xyz"
    invalid_file.touch()
    with pytest.raises(ValueError, match="Unsupported file format"):
        load_document(str(invalid_file))

def test_load_document_not_found():
    with pytest.raises(FileNotFoundError):
        load_document("non_existent_file.txt")

def test_text_splitter_basic():
    splitter = RecursiveCharacterTextSplitter(chunk_size=10, chunk_overlap=2)
    text = "abcdefghij"
    chunks = splitter.split_text(text)
    assert chunks == ["abcdefghij"]

def test_text_splitter_recursive():
    splitter = RecursiveCharacterTextSplitter(chunk_size=10, chunk_overlap=2)
    text = "hello\nworld\nhere\nare\nsome\nwords"
    chunks = splitter.split_text(text)
    for chunk in chunks:
        assert len(chunk) <= 10
    # Let's ensure the reconstructed text contains the original characters
    assert "".join(chunks).replace("\n", "").replace(" ", "") == text.replace("\n", "").replace(" ", "")

def test_text_splitter_overlap():
    splitter = RecursiveCharacterTextSplitter(chunk_size=20, chunk_overlap=5)
    text = "This is a sentence. And here is another one."
    chunks = splitter.split_text(text)
    for chunk in chunks:
        assert len(chunk) <= 20

def test_text_splitter_invalid_params():
    with pytest.raises(ValueError, match="chunk_overlap must be smaller than chunk_size"):
        RecursiveCharacterTextSplitter(chunk_size=10, chunk_overlap=10)


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, Document, DocumentChunk
from app.rag import store_document_chunks, query_similar_chunks

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/kotosensei")

@pytest.fixture(scope="module")
def db_engine():
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session(db_engine):
    connection = db_engine.connect()
    transaction = connection.begin()
    SessionLocal = sessionmaker(bind=connection)
    session = SessionLocal()
    yield session
    session.close()
    transaction.rollback()
    connection.close()

def test_store_and_query_similar_chunks(db_session):
    # 1. Create document
    doc = Document(title="Japanese Culture", content="This is a document about Japanese culture, tea ceremonies, and traditional music.")
    db_session.add(doc)
    db_session.commit()

    # 2. Add chunks and embeddings
    chunks = [
        "tea ceremony is a traditional Japanese ritual",
        "traditional music features the Koto instrument",
        "sushi is a popular Japanese food"
    ]
    embeddings = [
        [1.0] + [0.0]*383,
        [0.0, 1.0] + [0.0]*382,
        [0.0, 0.0, 1.0] + [0.0]*381
    ]

    # Store chunks
    store_document_chunks(db_session, doc.id, chunks, embeddings)

    # Verify they were stored
    db_chunks = db_session.query(DocumentChunk).filter(DocumentChunk.document_id == doc.id).all()
    assert len(db_chunks) == 3

    # Query similar chunks
    query_emb = [0.0, 0.9, 0.1] + [0.0]*381
    results = query_similar_chunks(db_session, query_emb, limit=2)

    assert len(results) == 2
    assert results[0].content == "traditional music features the Koto instrument"

def test_document_cascade_delete(db_session):
    doc = Document(title="Cascade Delete Test", content="Content to chunk")
    db_session.add(doc)
    db_session.commit()

    store_document_chunks(
        db_session,
        doc.id,
        ["Chunk 1", "Chunk 2"],
        [[0.1]*384, [0.2]*384]
    )

    # Verify they are stored
    assert db_session.query(DocumentChunk).filter(DocumentChunk.document_id == doc.id).count() == 2

    # Delete Document and verify chunks are cascade deleted
    db_session.delete(doc)
    db_session.commit()

    assert db_session.query(DocumentChunk).filter(DocumentChunk.document_id == doc.id).count() == 0

