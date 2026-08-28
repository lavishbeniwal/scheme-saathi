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
