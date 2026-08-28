# Scheme Saathi — Build Plan

## Week 1 — English RAG baseline

**Goal**: answer English questions about Indian government welfare schemes, grounded in real scheme documents, using a local vector store and a free LLM API. No Hindi translation yet — that's Week 2+ per CLAUDE.md's architecture (Hindi -> IndicTrans2 -> retrieve -> generate -> IndicTrans2 -> Hindi). This week covers the middle three steps only: retrieve -> generate, both in English.

### Scope

- Collect real content for 15-20 major central government welfare schemes (eligibility, benefits, required documents) from official sources (myscheme.gov.in where scrapable, ministry sites otherwise).
- Chunk each scheme's sections, embed with sentence-transformers, store in a local Chroma collection.
- Answer English questions via the Groq API, grounded only in retrieved chunks.
- Drive it from a CLI script — no Streamlit yet.

### Schemes covered

PM-KISAN, Ayushman Bharat (PM-JAY), PMAY-Gramin, PMAY-Urban, MGNREGA, PM Ujjwala Yojana, Sukanya Samriddhi Yojana, Atal Pension Yojana, PM Jan Dhan Yojana, PM Fasal Bima Yojana, PM Suraksha Bima Yojana, PM Jeevan Jyoti Bima Yojana, PM Matru Vandana Yojana, National Social Assistance Programme (NSAP), e-Shram, PM SVANidhi, Stand-Up India, Beti Bachao Beti Padhao.

Each scheme is a markdown file at `data/raw/<slug>.md` with four fixed sections: Overview, Eligibility, Benefits, Required Documents, plus a `Source:` line with the official URL(s) the content was drawn from. Where an official source didn't have a section's information, that section says so explicitly rather than guessing — those spots need manual follow-up before being treated as authoritative.

### File layout

```
data/raw/<slug>.md         Scheme documents (see above)
ingestion/loader.py         Parses data/raw/*.md into SchemeDoc {name, source_url, sections}
ingestion/chunker.py         SchemeDoc -> one Chunk per section, scheme name prefixed into chunk text
ingestion/build_index.py      Load -> chunk -> embed -> write to Chroma. Run this to (re)build the index.
rag/config.py                  Shared constants: embedding model, Chroma path/collection, Groq model, GROQ_API_KEY, top_k
rag/retriever.py                Embed a query, semantic search Chroma, return top-k chunks + metadata
rag/generator.py                 Build a grounded prompt from retrieved chunks, call Groq, return the answer
rag/pipeline.py                   answer_question(query) -> retrieve -> generate -> {answer, sources}
scripts/ask.py                     CLI: python -m scripts.ask "question"
```

### Design decisions

- **Embedding model**: `sentence-transformers/all-MiniLM-L6-v2` — free, local, fast, standard default.
- **Chunking**: one chunk per section (not fixed-size sliding windows), since each scheme document has four self-contained factual sections. Each chunk's text is prefixed with the scheme name so it still reads sensibly once retrieved out of context. Chunk metadata carries `scheme_name`, `section`, `source_url` for citation.
- **Vector store**: single Chroma collection (`scheme_docs`), persisted at `chroma_db/` (gitignored) via `PersistentClient`. `build_index.py` rebuilds the collection from scratch each run — idempotent, not incremental.
- **Generation**: Groq chat completion, model configured in `rag/config.py` (currently `openai/gpt-oss-120b` — re-check against Groq's live model list, via `client.models.list()`, if it starts erroring; free-tier model availability changes, and Llama 3.x models were removed from Groq's offering between when this plan was drafted and when it was implemented). The system prompt instructs the model to answer only from the provided context and say explicitly when something isn't covered, rather than filling gaps from general knowledge.
- **No LangChain/LlamaIndex**: the pipeline (load -> chunk -> embed -> store -> retrieve -> prompt -> generate) is simple enough to hand-roll directly against the `chromadb` and `groq` SDKs, keeping dependencies minimal.

### Running it

1. `pip install -r requirements.txt`
2. Copy `.env.example` to `.env` and set `GROQ_API_KEY`.
3. `python -m ingestion.build_index` — builds `chroma_db/` from `data/raw/`.
4. `python -m scripts.ask "What documents are required for PM-KISAN?"`

### Week 1 — Definition of Done

- [x] `python -m ingestion.build_index` completes without error and reports ~4 chunks x number of schemes indexed. (72 chunks from 18 schemes.)
- [x] `python -m scripts.ask` answers a PM-KISAN question correctly, citing PM-KISAN as the source.
- [x] Same for an Ayushman Bharat question and a PMAY question.
- [x] A question with no relevant scheme in the corpus gets a graceful "I don't have that information" response, not a fabricated answer.

Known rough edge: the `Sources:` line in `scripts/ask.py` output lists whatever chunks were retrieved (top-k nearest neighbors) even when the answer says "I don't know" — it's not filtered by whether the LLM actually used them. Not a plan violation (no similarity threshold was specified), but worth revisiting once real usage/eval data suggests a threshold.

---

## Environment notes — the transformers version pin

`requirements.txt` pins `transformers==4.51.3` and `sentence-transformers==5.7.0`
together. This is deliberate and load-bearing: do not upgrade either one
independently.

### The conflict

IndicTrans2 (planned for Hindi translation in a later week) is loaded through
HuggingFace `transformers` with `trust_remote_code=True`, and its remote code —
along with the `IndicTransToolkit` package that supplies the tokenizer and
pre/post-processing — targets the `transformers` 4.x API. On `transformers`
5.16.1 it fails in three separate places: `IndicTransToolkit` imports
`PreTrainedTokenizerBase` from a module 5.x moved it out of; the model's
`configuration_indictrans.py` imports `transformers.onnx`, removed entirely in
5.x; and `IndicTransTokenizer.__init__` assigns special tokens in an order 5.x's
base class rejects. `transformers` 4.57.6 also fails, in the decoder's KV-cache
handling. `transformers==4.51.3` is the version that actually works.

The complication is that retrieval already depends on `sentence-transformers`,
and version 6.0.0 declares `transformers<6.0.0,>=5.0.0` — directly incompatible
with the 4.51.3 that IndicTrans2 needs.

### Options considered

1. **Two-process split** — run translation in its own virtualenv behind a small
   local HTTP service, keeping retrieval on `transformers` 5.x. Correct but adds
   a process boundary, a serialization layer, and a second environment to keep
   installed and running for what is otherwise a single-user local app.
2. **Override the declared conflict** — force `transformers==4.51.3` alongside
   `sentence-transformers==6.0.0` and rely on it working in practice. It does
   work for the code paths the Week 1 checks exercise, but leaves
   `sentence-transformers` running outside its declared support range, with a pip
   conflict warning on every install and no guarantee about untested paths.
3. **Find a `sentence-transformers` that supports both** (chosen). PyPI metadata
   shows the requirement changed only at 6.0.0: releases 5.2.0 through **5.7.0**
   declare `transformers<6.0.0,>=4.41.0`, which admits 4.51.3. So
   `sentence-transformers==5.7.0` — the newest release before the bump — supports
   the exact `transformers` IndicTrans2 needs.

Option 3 won because it needs no process boundary and no override: every package
runs inside its own declared, supported range. `pip check` reports "No broken
requirements found", and installs produce no conflict warnings.

### Validation evidence

Checked in a throwaway clone of the venv first, then re-confirmed on the real one
after applying the change:

- **Embeddings are byte-identical across all three configurations.** Encoding a
  fixed set of strings with `all-MiniLM-L6-v2` produces SHA-256
  `a9f762292403a1e824885c870cc47cc68c3f3c28dbb8cdbf315f33cd3648f99b` under
  `sentence-transformers` 6.0.0 + `transformers` 5.16.1, under 6.0.0 + 4.51.3, and
  under 5.7.0 + 4.51.3. Retrieval behaviour is therefore unchanged, and the
  existing `chroma_db/` index stays valid — no reindexing needed after the
  downgrade.
- **All four Week 1 Definition-of-Done checks pass** on the pinned combination:
  `build_index` produces the same 72 chunks from 18 schemes, the PM-KISAN,
  Ayushman Bharat and PMAY questions answer correctly, and the out-of-corpus
  question still refuses gracefully instead of fabricating. The retrieved
  `Sources:` lists are identical to the pre-change baseline for all four
  questions.
- **IndicTrans2 runs in the same environment**, both directions, CPU-only on
  native Windows — roughly 0.7-1.9s per sentence and about 1.4 GB peak RSS with
  both distilled 200M checkpoints loaded.

### Practical notes for later weeks

- `sentencepiece` is pinned explicitly because `IndicTransToolkit` does not
  declare it, but the IndicTrans2 tokenizer imports it directly — an unpinned
  install would fail only at translation time.
- The AI4Bharat checkpoints are **gated** on HuggingFace: a logged-in account
  (`hf auth login`) that has accepted the model terms is required before they can
  be downloaded.
- Native Windows works; the WSL2 setup that AI4Bharat's docs imply is not needed.
- Anything printing Hindi needs `sys.stdout.reconfigure(encoding="utf-8")` —
  Windows consoles default to cp1252 and raise `UnicodeEncodeError` on Devanagari.
  `scripts/ask.py` already does this.

---

## Later weeks (not yet planned in detail)

- Hindi translation at the edges (IndicTrans2): Hindi question -> English -> ... -> English answer -> Hindi.
- Streamlit frontend.
- RAGAS evaluation (`evaluation/ragas_eval.py`, wired to the `run-eval` skill).
