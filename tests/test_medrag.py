from pathlib import Path

from medrag.answer import AnswerService
from medrag.config import Settings
from medrag.ingest import write_index
from medrag.types import Chunk


def service(tmp_path: Path) -> AnswerService:
    index = tmp_path / "index.db"
    write_index([Chunk("1", "Headache", "Headache: Rest and drink water.", "https://example.test/headache", "MedlinePlus, National Library of Medicine", "2026-01-01")], index)
    return AnswerService(Settings(index_path=index))


def test_answer_has_citation(tmp_path):
    result = service(tmp_path).answer("What can help with a headache?")
    assert result.status == "answered"
    assert "[1]" in result.text
    assert result.citations[0].chunk.title == "Headache"


def test_emergency_bypasses_retrieval(tmp_path):
    result = service(tmp_path).answer("I have chest pain")
    assert result.status == "emergency"
    assert "999" in result.text
    assert not result.citations


def test_personal_diagnosis_abstains(tmp_path):
    result = service(tmp_path).answer("Do I have a serious illness?")
    assert result.status == "out_of_scope"

