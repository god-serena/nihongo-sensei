import os
import pytest
import tempfile
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base
from app.ingest_dictionary import ingest
from app.dictionaries.jmdict import JMdictProvider

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/kotosensei")

MOCK_JMDICT_XML = """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE JMdict SYSTEM "JMdict.dtd" [
<!ENTITY n "noun (common) (futsuumeishi)">
]>
<JMdict>
  <entry>
    <ent_seq>1000001</ent_seq>
    <k_ele>
      <keb>日本語</keb>
    </k_ele>
    <r_ele>
      <reb>にほんご</reb>
    </r_ele>
    <sense>
      <pos>&n;</pos>
      <gloss>Japanese language</gloss>
    </sense>
  </entry>
  <entry>
    <ent_seq>1000002</ent_seq>
    <k_ele>
      <keb>琴</keb>
    </k_ele>
    <r_ele>
      <reb>こと</reb>
    </r_ele>
    <sense>
      <pos>&n;</pos>
      <gloss>koto (13-stringed Japanese zither)</gloss>
    </sense>
  </entry>
</JMdict>
"""

@pytest.fixture(scope="module")
def db_engine():
    engine = create_engine(DATABASE_URL)
    # Ensure tables are created
    Base.metadata.create_all(bind=engine)
    yield engine
    # Clean up tables
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

def test_dictionary_ingestion_and_lookup(db_session):
    # Ingest the mock XML data into the test database
    with tempfile.NamedTemporaryFile(suffix=".xml", delete=False, mode="w", encoding="utf-8") as f:
        f.write(MOCK_JMDICT_XML)
        temp_filename = f.name

    try:
        # Run ingestion
        ingest(temp_filename)

        # Create provider
        provider = JMdictProvider(db_session)

        # Test lookup by kanji
        res = provider.lookup("日本語")
        assert res["term"] == "日本語"
        assert len(res["entries"]) == 1
        assert res["entries"][0]["sequence_number"] == "1000001"
        assert "日本語" in res["entries"][0]["kanji"]
        assert "にほんご" in res["entries"][0]["reading"]
        assert res["entries"][0]["senses"][0]["glosses"] == ["Japanese language"]
        assert "n" in res["entries"][0]["senses"][0]["parts_of_speech"]

        # Test lookup by reading
        res_reading = provider.lookup("こと")
        assert res_reading["term"] == "こと"
        assert len(res_reading["entries"]) == 1
        assert res_reading["entries"][0]["sequence_number"] == "1000002"
        assert "琴" in res_reading["entries"][0]["kanji"]
        assert res_reading["entries"][0]["senses"][0]["glosses"] == ["koto (13-stringed Japanese zither)"]
        assert "n" in res_reading["entries"][0]["senses"][0]["parts_of_speech"]

        # Test lookup with no match
        res_empty = provider.lookup("三味線")
        assert res_empty["term"] == "三味線"
        assert len(res_empty["entries"]) == 0

    finally:
        os.unlink(temp_filename)
