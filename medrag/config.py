from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    index_path: Path = Path("data/index.db")
    top_k: int = 5
    min_score: float = 0.08
    locale: str = "UK"
    model: str = "extractive"
    log_queries: bool = False

