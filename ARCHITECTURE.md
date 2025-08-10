# Architecture

This document describes the repository structure and component interactions for V001–V004.

## Repository Structure

```
app/
  cli.py                 # CLI entrypoint for run/eval/ingest/deep
  agents/                # Agent implementations per version
  config/                # Layered YAML configs: defaults + version + profiles
  prompts/               # Versioned agent/planner/judge prompts
  tools/                 # Search, retriever, ingestion utilities
  orchestration/         # Planner, dialogue, executor, blackboard (V004)
  retrieval/             # Backends, chunking, embeddings, manifests (V003)
  evaluation/            # Datasets, judges, metrics, runner, reporting
  logging/               # Logging setup for structured logs

data/
  sources/               # Raw docs per company (local only)
  indexes/               # Vector indexes by company/version (gitignored)

artifacts/
  runs/                  # Run outputs (answers, contexts, judgments)
```

## High-Level Component Diagram

```mermaid
flowchart TD
  A["User CLI"] --> B{Mode}
  B -->|"v001"| C["Agent V001"]
  B -->|"v002"| D["Agent V002"]
  B -->|"v003"| E["Agent V003"]
  B -->|"v004"| F["Agent V004"]

  subgraph Core["Core App"]
    C --> G["Model"]
    D --> G
    E --> G
    F --> G
  end

  G --> H["Search Tool"]
  G --> I["Retriever"]
  G --> J["Index"]

  subgraph Tools
    H
    I
    J
  end

  subgraph Orchestration
    F --> K["Planner"]
    F --> L["Dialogue Manager"]
    F --> M["Executor/Blackboard"]
  end

  subgraph Evaluation
    N["Evaluation Runner"] --> O["LLM Judge"]
    N --> P["MLflow"]
  end

  A --> N
  H -.-> Q[("Web")]
  J -.-> R[("Data/Indexes")]
```

## Version-Specific Flows

### V002: Search Deep Research
```mermaid
sequenceDiagram
  participant U as User
  participant A as Agent V002
  participant S as Search Tool
  participant M as Model

  U->>A: question, company
  A->>S: search queries (throttled, retries)
  S-->>A: results (title, url, snippet)
  A->>M: synthesize with citations
  M-->>A: answer text
  A-->>U: answer + citations
```

### V003: Retrieval-Augmented Generation (RAG)
```mermaid
sequenceDiagram
  participant U as User
  participant A as Agent V003
  participant R as Retriever
  participant X as Index
  participant M as Model

  U->>A: question, company
  A->>R: retrieve top_k with threshold
  R->>X: vector search
  X-->>R: passages + scores
  R-->>A: context pack
  A->>M: constrained synthesis with context
  M-->>A: answer text
  A-->>U: answer + citations
```

### V004: Deep Planning + Clarification
```mermaid
sequenceDiagram
  participant U as User
  participant P as Planner
  participant D as Dialogue
  participant E as Executor
  participant R as Retriever
  participant S as Search
  participant M as Model

  U->>P: goal (company, question)
  P-->>E: task graph (budgets)
  alt missing info
    E->>D: request clarification
    D->>U: ask targeted question
    U-->>D: answer
  end
  par info collection
    E->>R: retrieve RAG
    E->>S: web search
  end
  E->>M: synthesize using blackboard
  M-->>E: answer
  E-->>U: answer + citations + assumptions
```

## Data Schemas (abridged)

- Evidence (blackboard):
```json
{
  "evidence_id": "uuid",
  "type": "rag|web|user",
  "text": "...",
  "source_uri": "doc://... | https://...",
  "score": 0.82,
  "timestamp": "ISO-8601",
  "provenance": {"company": "Acme", "chunk_id": "12"}
}
```

- Plan (V004):
```json
{
  "plan": [
    {"id": "step-1", "type": "retrieve_rag", "inputs": {"query": "..."}},
    {"id": "step-2", "type": "search_web", "when": "if recall low"},
    {"id": "step-3", "type": "ask_user", "when": "if ambiguity blocks synthesis"},
    {"id": "step-4", "type": "synthesize"}
  ],
  "budgets": {"max_steps": 20, "max_questions": 3}
}
```

- Retrieval Passage (V003):
```json
{
  "text": "...",
  "source_uri": "doc://kb/acme/overview.md",
  "chunk_id": "1",
  "score": 0.85,
  "metadata": {"company": "acme"}
}
```

## Notes
- Prompts are versioned and referenced by agents; planner prompt outputs structured JSON.
- Config layering: defaults -> version -> profile -> CLI overrides.
- Index manifests capture embedding/chunk settings for reproducibility.
