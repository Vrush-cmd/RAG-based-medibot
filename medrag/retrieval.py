import re
import sqlite3
from pathlib import Path

from .types import Chunk, Hit

STOPWORDS = {
    "a", "an", "and", "are", "can", "do", "for", "how", "i", "is", "it",
    "me", "of", "on", "or", "the", "this", "to", "was", "what", "with",
    "why", "you",
}


class Retriever:
    def __init__(self, index_path: Path):
        self.index_path = index_path

    def search(self, query: str, limit: int = 5) -> list[Hit]:
        terms = [term for term in re.findall(r"[a-z0-9]+", query.lower()) if term not in STOPWORDS]
        if not terms or not self.index_path.exists():
            return []
        match = " OR ".join(f'"{term}"' for term in terms)
        with sqlite3.connect(self.index_path) as db:
            rows = db.execute("""
                SELECT c.id, c.title, c.text, c.url, c.source, c.file_date, bm25(search) AS score
                FROM search JOIN chunks c ON c.id = search.id
                WHERE search MATCH ? ORDER BY score LIMIT ?
            """, (match, limit)).fetchall()
        if not rows:
            return []
        best = min(float(row[-1]) for row in rows)
        hits = []
        for row in rows:
            raw = float(row[-1])
            score = max(0.0, (raw / best) if best < 0 else 0.0)
            hits.append(Hit(Chunk(*row[:-1]), score))
        return hits

