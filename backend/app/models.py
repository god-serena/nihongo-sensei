import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON, Index
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.dialects.postgresql import JSONB
from pgvector.sqlalchemy import Vector


Base = declarative_base()


class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=True)
    messages = Column(JSONB, nullable=False, default=list)
    jlpt_level = Column(String(10), default="N4")
    teaching_mode = Column(String(20), default="bilingual")
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
        nullable=False,
    )

    summaries = relationship(
        "SessionSummary", back_populates="session", cascade="all, delete-orphan"
    )


class SessionSummary(Base):
    __tablename__ = "session_summaries"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    summary_data = Column(JSON, nullable=False)  # structured JSON (topics, new vocab, mistakes)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    session = relationship("Session", back_populates="summaries")


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(384), nullable=False)

    document = relationship("Document", back_populates="chunks")


class DictionaryEntry(Base):
    __tablename__ = "dictionary_entries"

    id = Column(Integer, primary_key=True, index=True)
    sequence_number = Column(String(50), nullable=True)
    kanji = Column(JSONB, nullable=False, default=list)
    reading = Column(JSONB, nullable=False, default=list)
    senses = Column(JSONB, nullable=False, default=list)


# Add GIN indexes for fast lookup on JSONB lists
Index("ix_dictionary_entries_kanji_gin", DictionaryEntry.kanji, postgresql_using="gin")
Index("ix_dictionary_entries_reading_gin", DictionaryEntry.reading, postgresql_using="gin")
