"""MedRAG UI.

Run ``python app.py`` for the zero-dependency local UI. If Streamlit is
installed, ``streamlit run app.py`` still provides the richer interface.
"""
from html import escape
import os
from pathlib import Path
from urllib.parse import parse_qs, urlparse
from http.server import BaseHTTPRequestHandler, HTTPServer

try:
    import streamlit as st
except ImportError as exc:  # pragma: no cover
    st = None

from medrag.answer import AnswerService
from medrag.config import Settings

if st:
    st.set_page_config(page_title="MedRAG", page_icon="🩺")
    st.title("MedRAG")
    st.caption("General health information from curated NIH sources — not medical advice.")
    st.info("Do not enter names, dates of birth, record numbers, or other identifying information.")
    question = st.chat_input("Ask a general health-information question")
    if question:
        result = AnswerService(Settings(index_path=Path("data/index.db"))).answer(question)
        with st.chat_message("assistant"):
            st.write(result.text)
            for n, hit in enumerate(result.citations, 1):
                st.markdown(f"**[{n}] {hit.chunk.title}** — {hit.chunk.source} ({hit.chunk.file_date})  ")
                if hit.chunk.url:
                    st.markdown(hit.chunk.url)
    st.caption("Information from NIH sources, not medical advice. In an emergency call your local emergency number.")


def _page(question: str = "", answer: str = "") -> bytes:
    return f"""<!doctype html>
<html><head><meta name=viewport content='width=device-width, initial-scale=1'>
<title>MedRAG</title><style>body{{font:16px system-ui;max-width:760px;margin:40px auto;padding:0 18px;color:#202124}}textarea{{width:100%;min-height:90px;padding:12px;font:inherit}}button{{margin-top:12px;padding:10px 18px}}.notice{{background:#f1f3f4;padding:14px;border-radius:8px}}.answer{{white-space:pre-wrap;margin-top:24px}}</style></head>
<body><h1>MedRAG</h1><p>General health information from curated NIH sources — not medical advice.</p>
<p class=notice>Do not enter names, dates of birth, record numbers, or other identifying information.</p>
<form method=post><textarea name=question placeholder='Ask a general health-information question'>{escape(question)}</textarea><br><button>Ask</button></form>
{f'<div class=answer><h2>Answer</h2>{escape(answer)}</div>' if answer else ''}
<p><small>Information from NIH sources, not medical advice. In an emergency call your local emergency number.</small></p></body></html>""".encode()


class _Handler(BaseHTTPRequestHandler):
    def _respond(self, body: bytes) -> None:
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        self._respond(_page())

    def do_POST(self) -> None:  # noqa: N802
        size = int(self.headers.get("Content-Length", "0"))
        question = parse_qs(self.rfile.read(size).decode()).get("question", [""])[0].strip()
        result = AnswerService(Settings(index_path=Path("data/index.db"))).answer(question) if question else None
        answer = result.text if result else ""
        if result and result.citations:
            answer += "\n\n" + "\n".join(f"[{i}] {h.chunk.title} — {h.chunk.source}" for i, h in enumerate(result.citations, 1))
        self._respond(_page(question, answer))

    def log_message(self, *_args) -> None:
        return


if __name__ == "__main__" and not st:
    port = int(os.environ.get("MEDRAG_PORT", "8501"))
    print(f"MedRAG running at http://127.0.0.1:{port} (Ctrl-C to stop)")
    HTTPServer(("127.0.0.1", port), _Handler).serve_forever()

