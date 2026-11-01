from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from .config import Settings
from .retrieval import Retriever
from .safety import safety_check
from .types import Answer, Hit


class Generator(Protocol):
    def generate(self, question: str, hits: list[Hit]) -> str: ...


class ExtractiveGenerator:
    """Safe local fallback: it can only return retrieved sentences."""
    def generate(self, question: str, hits: list[Hit]) -> str:
        sentences = []
        for hit in hits[:3]:
            body = hit.chunk.text.split(": ", 1)[-1]
            sentences.extend(part.strip() for part in body.replace("\n", " ").split(". ") if part.strip())
        selected = sentences[:3]
        if not selected:
            return "I can't find this in my sources."
        return " ".join(sentence.rstrip(".") + f" [{i + 1}]." for i, sentence in enumerate(selected))


@dataclass
class AnswerService:
    settings: Settings
    generator: Generator | None = None

    def __post_init__(self) -> None:
        self.retriever = Retriever(self.settings.index_path)
        self.generator = self.generator or ExtractiveGenerator()

    def answer(self, question: str) -> Answer:
        kind, notice = safety_check(question)
        if kind != "ok":
            return Answer(notice or "Please seek appropriate help.", [], kind, notice)
        hits = self.retriever.search(question, self.settings.top_k)
        if not hits or hits[0].score < self.settings.min_score:
            return Answer("I can't find this in my sources. Please speak with a clinician for personal advice.", hits, "abstained")
        evidence = hits[:3]
        text = self.generator.generate(question, evidence)
        return Answer(text, evidence, "answered")

