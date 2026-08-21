# GW Pathfinder: System Design

*Draft section — design/architecture only. Not built as part of this thesis; documented here to show how the estimation work (Section on chirp-mass feasibility) fits into the larger project.*

## 1. Purpose

GW Pathfinder is an educational query tool over gravitational-wave circulars and events: a user asks a natural-language question about a GW event or class of events, and the system answers grounded in structured, retrieved data rather than an LLM's unaided memory. The chirp-mass estimator developed in this thesis is one inference module within this system, not a separate deliverable.

## 2. Why grounding matters here

The AI-model comparison study (a separate, ongoing leg of this project) found that general-purpose LLMs, asked to recall GW event parameters (masses, references, catalog membership) from memory alone, gave inconsistent and partial results across models — reliable for some well-known events, unreliable or fabricated for others, and none could guarantee numeric accuracy without checking a source. This motivates Pathfinder's core design constraint: **answers must be grounded in retrieved structured data, not generated from model memory.**

## 3. Architecture

```
GCN circular text
      │
      ▼
Ingestion + parsing (src/ingestion, src/parsing, src/processing)
      │  → structured event table with provenance
      │     (already built for the estimation work — shared, not duplicated)
      ▼
Embedding + indexing
      │  → per-event / per-circular vector embeddings, indexed for retrieval
      ▼
Retrieval
      │  → given a query, fetch the relevant structured records + source circular text
      ▼
LLM response layer
      │  → summarizes/answers using only retrieved records; cites source circular IDs
      ▼
Inference modules (pluggable)
      │  → e.g. chirp-mass estimator (src/modeling/statistical_estimator.py),
      │     invoked when a user asks about mass for an event with no directly
      │     reported value — response is explicitly labeled as an estimate
```

## 4. Components

- **Ingestion & parsing layer** — reuses the pipeline already built for the estimation work (`src/ingestion`, `src/parsing`, `src/processing`). The same structured event table (distance, FAR, classification, reference chirp mass where available, provenance) feeds both the estimator and Pathfinder's retrieval index, so this is shared infrastructure, not separate work.
- **Embedding & retrieval layer** — circular text and/or structured event summaries embedded (e.g. sentence-transformers) and indexed for vector search, enabling queries like "show me BBH events from O4a with distance under 500 Mpc" without exact keyword matching.
- **Inference modules** — the chirp-mass estimator is exposed as a callable module Pathfinder can invoke for events lacking a directly reported chirp mass. Any such response must state the estimation method and its known error characteristics (Section on estimator results), not present the estimate as a measurement.
- **LLM response layer** — summarization and Q&A constrained to retrieved records, with source circular IDs cited, directly addressing the reliability gap the comparison study identified in unaided LLM recall.

## 5. Status

Design only. No embedding, retrieval, or chatbot code has been built as part of this thesis draft. The ingestion/parsing/processing layers it would reuse are already implemented and tested (Section on data pipeline).

## 6. Open design questions

- Embed raw circular text, or the structured per-event summary (or both)?
- Local embedding model vs. an API-based one — affects reproducibility and cost.
- How to handle events with conflicting circular reports (already partially addressed by the estimation pipeline's provenance/confidence logic — reusable here).
