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
