# MedRAG — Personal AI Medical Assistant

MedRAG is a local, single-user question-answering assistant for general health information. It retrieves passages from curated NIH-sourced content, answers only from that evidence, and exposes numbered source citations. It is an information tool, not a medical device: it does not diagnose, prescribe, triage, or replace a clinician.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'

# Rebuild the complete local index from raw downloads.
python -m medrag.cli ingest --medlineplus path/to/health-topics.xml --out data/index.db
python -m medrag.cli ask "What can help with a headache?"
```

The ingestion command also accepts a MedQuAD-style JSON file with `--medquad`. It indexes answer text only, keeps source metadata and file dates, de-duplicates MedlinePlus URLs, and stores the index in SQLite. No source data or query log is committed.

The optional UI is available with `pip install -e '.[ui]'` followed by `streamlit run app.py`.

## Safety and privacy

Urgent red flags are checked before retrieval. Chest pain, breathing trouble, stroke signs, severe bleeding, overdose/poisoning, severe allergic reaction, and self-harm prompts receive an emergency response rather than a generated answer. Personal diagnosis, dosing, interaction checks, and pregnancy/paediatric dosing are out of scope and are redirected to a clinician, pharmacist, or product label.

The default generator is extractive and therefore cannot invent facts. A future hosted-model adapter must treat retrieved passages as untrusted data, require `[n]` citations, and pass a faithfulness check before its text is shown. Queries and retrieved passages may leave the machine only when a hosted adapter is explicitly configured; do not enter identifying information. Query logging is off by default.

## Sources and attribution

The intended primary source is MedlinePlus Health Topics XML, from the U.S. National Library of Medicine/NIH. MedQuAD is an optional secondary NIH-sourced dataset and its questions remain evaluation-only. Re-check each source’s licence before publishing or hosting the index, especially any non-commercial/no-derivatives source. The UI and CLI carry: “Information from NIH sources, not medical advice. In an emergency call your local emergency number.”

## Evaluation direction

Keep a frozen MedQuAD test set separate from ingestion questions. Measure retrieval hit@k, MRR and recall@k before generation; then measure faithfulness, answer relevance, context precision/recall, abstention, and red-flag coverage. Compare against the same model without retrieval. Every run should record the configuration, commit, source file date, and a small hand-reviewed failure sample.

See the ignored [interview-prep.md](docs/interview-prep.md) for the architecture walkthrough, trade-offs, and likely interview questions.
