from abc import ABC, abstractmethod

class DictionaryProvider(ABC):
    @abstractmethod
    def lookup(self, term: str) -> dict:
        """
        Perform an exact-match lookup for a term (kanji or reading).
        Returns a dict representing the entry.
        """
        pass
