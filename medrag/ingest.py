from __future__ import annotations

import hashlib
from html import unescape
import json
import re
import sqlite3
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path
from typing import Iterable

from .types import Chunk


def _clean(value: str) -> str:
    value = re.sub(r"<[^>]+>", " ", unescape(value or ""))
    return re.sub(r"\s+", " ", value).strip()


def chunk_text(title: str, text: str, *, size: int = 900, overlap: int = 120) -> list[str]:
    words = _clean(text).split()
    if not words:
        return []
    result = []
    start = 0
    while start < len(words):
        body = " ".join(words[start : start + size])
        result.append(f"{title}: {body}")
        if start + size >= len(words):
            break
        start += size - overlap
    return result


def medlineplus_xml(path: Path, file_date: str | None = None) -> Iterable[Chunk]:
    """Parse common MedlinePlus health-topic XML exports without third-party deps."""
    root = ET.parse(path).getroot()
    seen: set[str] = set()
    stamp = file_date or date.today().isoformat()
    for topic in root.findall("health-topic"):
        if topic.attrib.get("language", "English") != "English":
            continue
        title = _clean(topic.attrib.get("title", ""))
        url = _clean(topic.attrib.get("url", ""))
        body = _clean(topic.findtext("full-summary") or topic.attrib.get("meta-desc", ""))
        if not title or not body or (url and url in seen):
            continue
        if url:
            seen.add(url)
        for n, text in enumerate(chunk_text(title, body)):
            ident = hashlib.sha256(f"{url}|{n}|{text}".encode()).hexdigest()[:20]
            yield Chunk(ident, title, text, url, "MedlinePlus, National Library of Medicine", stamp)


def json_documents(path: Path, file_date: str | None = None) -> Iterable[Chunk]:
    """Parse a permissive MedQuAD-style JSON list; question text is deliberately ignored."""
    stamp = file_date or date.today().isoformat()
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        data = data.get("documents", data.get("data", []))
    for item in data:
        title = _clean(str(item.get("title") or item.get("document_id") or "MedQuAD"))
        text = _clean(str(item.get("answer") or item.get("text") or ""))
        url = _clean(str(item.get("url") or item.get("source_url") or ""))
        for n, body in enumerate(chunk_text(title, text)):
            ident = hashlib.sha256(f"{url}|{n}|{body}".encode()).hexdigest()[:20]
            yield Chunk(ident, title, body, url, "MedQuAD", stamp)


def write_index(chunks: Iterable[Chunk], destination: Path) -> int:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(destination) as db:
        db.executescript("""
            DROP TABLE IF EXISTS chunks;
            CREATE TABLE chunks (id TEXT PRIMARY KEY, title TEXT NOT NULL, text TEXT NOT NULL,
                url TEXT, source TEXT NOT NULL, file_date TEXT NOT NULL);
            DROP TABLE IF EXISTS search;
            CREATE VIRTUAL TABLE search USING fts5(id UNINDEXED, title, text, source);
        """)
        count = 0
        for chunk in chunks:
            db.execute("INSERT INTO chunks VALUES (?, ?, ?, ?, ?, ?)", tuple(chunk.__dict__.values()))
            db.execute("INSERT INTO search VALUES (?, ?, ?, ?)", (chunk.id, chunk.title, chunk.text, chunk.source))
            count += 1
        db.commit()
    return count

