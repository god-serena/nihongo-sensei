import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, Session, SessionSummary, Document

DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/kotosensei"
)


@pytest.fixture(scope="module")
def db_engine():
    engine = create_engine(DATABASE_URL)
    # Ensure tables are created
    Base.metadata.create_all(bind=engine)
    yield engine
    # Clean up
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


def test_crud_session(db_session):
    # Create
    new_session = Session(title="Test Japanese Lesson")
    db_session.add(new_session)
    db_session.commit()

    assert new_session.id is not None

    # Read
    fetched = db_session.query(Session).filter(Session.id == new_session.id).first()
    assert fetched is not None
    assert fetched.title == "Test Japanese Lesson"

    # Update
    fetched.title = "Updated Lesson"
    db_session.commit()

    updated = db_session.query(Session).filter(Session.id == new_session.id).first()
    assert updated.title == "Updated Lesson"

    # Delete
    db_session.delete(updated)
    db_session.commit()

    deleted = db_session.query(Session).filter(Session.id == new_session.id).first()
    assert deleted is None


def test_session_summary_cascade(db_session):
    # Create session
    new_session = Session(title="Cascade Test Session")
    db_session.add(new_session)
    db_session.commit()

    # Create summary
    summary_data = {
        "topics": ["Grammar ~te form", "Vocabulary"],
        "new_vocab": ["琴", "日本語"],
        "mistakes": ["Incorrect particle usage"],
    }
    summary = SessionSummary(session_id=new_session.id, summary_data=summary_data)
    db_session.add(summary)
    db_session.commit()

    assert summary.id is not None

    # Check relation
    assert len(new_session.summaries) == 1
    assert new_session.summaries[0].summary_data["new_vocab"] == ["琴", "日本語"]

    # Delete session and check cascade delete on summary
    db_session.delete(new_session)
    db_session.commit()

    deleted_summary = (
        db_session.query(SessionSummary).filter(SessionSummary.id == summary.id).first()
    )
    assert deleted_summary is None


def test_document_crud(db_session):
    # Create
    doc = Document(title="Article on Hiragana", content="This is content about Hiragana history...")
    db_session.add(doc)
    db_session.commit()

    assert doc.id is not None

    # Read
    fetched = db_session.query(Document).filter(Document.id == doc.id).first()
    assert fetched is not None
    assert fetched.title == "Article on Hiragana"

    # Delete
    db_session.delete(fetched)
    db_session.commit()

    deleted = db_session.query(Document).filter(Document.id == doc.id).first()
    assert deleted is None
