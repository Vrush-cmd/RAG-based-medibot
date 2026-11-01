import argparse
import json
from pathlib import Path

from .answer import AnswerService
from .config import Settings
from .ingest import json_documents, medlineplus_xml, write_index


def main() -> None:
    parser = argparse.ArgumentParser(prog="medrag")
    sub = parser.add_subparsers(dest="command", required=True)
    ingest = sub.add_parser("ingest", help="Build the local index from raw source files")
    ingest.add_argument("--medlineplus", type=Path)
    ingest.add_argument("--medquad", type=Path)
    ingest.add_argument("--out", type=Path, default=Path("data/index.db"))
    ask = sub.add_parser("ask", help="Ask a cited question")
    ask.add_argument("question")
    ask.add_argument("--index", type=Path, default=Path("data/index.db"))
    args = parser.parse_args()
    if args.command == "ingest":
        chunks = []
        if args.medlineplus:
            chunks.extend(medlineplus_xml(args.medlineplus))
        if args.medquad:
            chunks.extend(json_documents(args.medquad))
        if not chunks:
            parser.error("provide --medlineplus and/or --medquad")
        print(json.dumps({"chunks": write_index(chunks, args.out), "index": str(args.out)}))
    else:
        answer = AnswerService(Settings(index_path=args.index)).answer(args.question)
        print(answer.text)
        for n, hit in enumerate(answer.citations, 1):
            print(f"[{n}] {hit.chunk.title} — {hit.chunk.source} ({hit.chunk.file_date}) {hit.chunk.url}")
        print("\nInformation from NIH sources, not medical advice. In an emergency call your local emergency number.")


if __name__ == "__main__":
    main()

