from sqlalchemy.orm import Session
from app.dictionaries.base import DictionaryProvider
from app.models import DictionaryEntry

class JMdictProvider(DictionaryProvider):
    def __init__(self, db: Session):
        self.db = db

    def lookup(self, term: str) -> dict:
        """
        Perform an exact-match lookup for a term (kanji or reading).
        Returns a dict containing the term and the matching entries:
        {
            "term": term,
            "entries": [
                {
                    "sequence_number": str,
                    "kanji": list[str],
                    "reading": list[str],
                    "senses": list[dict]
                },
                ...
            ]
        }
        """
        # Search for term in the kanji or reading JSONB lists
        entries = self.db.query(DictionaryEntry).filter(
            (DictionaryEntry.kanji.contains([term])) |
            (DictionaryEntry.reading.contains([term]))
        ).all()

        return {
            "term": term,
            "entries": [
                {
                    "sequence_number": entry.sequence_number,
                    "kanji": entry.kanji,
                    "reading": entry.reading,
                    "senses": entry.senses
                }
                for entry in entries
            ]
        }
