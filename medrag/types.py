from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Chunk:
    id: str
    title: str
    text: str
    url: str
    source: str
    file_date: str


@dataclass(frozen=True)
class Hit:
    chunk: Chunk
    score: float


@dataclass(frozen=True)
class Answer:
    text: str
    citations: list[Hit]
    status: str = "answered"
    safety_notice: str | None = None

