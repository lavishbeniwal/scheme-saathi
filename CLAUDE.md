# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

Scheme Saathi is a semester-long solo project: a Hindi-language RAG (retrieval-augmented generation) assistant that answers questions about Indian government welfare schemes.

## Architecture

Request flow:

1. User asks a question in Hindi.
2. Translate the question to English with IndicTrans2.
3. Retrieve relevant scheme documents from the vector store.
4. Generate an answer with an LLM, grounded in the retrieved documents.
5. Translate the generated answer back to Hindi before returning it to the user.

All translation happens at the edges (Hindi -> English on the way in, English -> Hindi on the way out); retrieval and generation both operate in English.

## Stack

Everything in the stack is free-tier / local — no paid AWS services for now.

- **LLM**: Groq API
- **Embeddings**: sentence-transformers
- **Vector store**: Chroma (local, on-disk)
- **Translation**: IndicTrans2 (Hindi <-> English, both directions)
- **Evaluation**: RAGAS
- **Frontend**: Streamlit

## Environment

- `GROQ_API_KEY` must be set (see `.env.example`) for LLM calls to work.

## Commands

- Install deps: `pip install -r requirements.txt`
- Build/rebuild the vector index from `data/raw/`: `python -m ingestion.build_index`
- Ask a question (English only, Week 1): `python -m scripts.ask "your question"`
- Run scripts as modules (`python -m ...`) from the repo root, not as bare file paths — the `rag`, `ingestion`, and `scripts` packages resolve via the repo root being on `sys.path`.

## Code architecture

- `data/raw/*.md` — one file per welfare scheme, with fixed `## Overview` / `## Eligibility` / `## Benefits` / `## Required Documents` sections plus a `Source:` line. `ingestion/loader.py` parses this exact structure, so new scheme files must follow it.
- `ingestion/build_index.py` — rebuilds the Chroma collection from scratch each run (not incremental): load scheme files -> chunk one-per-section -> embed with sentence-transformers -> write to `chroma_db/`.
- `rag/pipeline.py` — the request-time path: `retriever.py` embeds the query and searches Chroma, `generator.py` builds a context-grounded prompt and calls Groq. The generator's system prompt is instructed to answer only from retrieved context and say so when it can't — don't relax this without a reason, it's what keeps eligibility/benefit answers from being hallucinated.
- See `PLAN.md` for the current week's scope and design decisions; it's the reference the `reviewer` subagent checks code against.
