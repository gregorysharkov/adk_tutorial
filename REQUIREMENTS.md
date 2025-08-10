# Agentic Systems Evaluation Framework

Build an agent using Google ADK to answer user questions about specific companies and evaluate its performance across versions.

## 1. Overview and Objectives
- Goal: Provide accurate, grounded answers about companies using a tool-augmented agent and measure quality.
- Objectives:
  - V001 (MVP): Single-model console agent that answers user questions.
  - V002 (POC): Tool-augmented agent using Google Search to perform “deep research” before answering.
  - V003 (RAG): Retrieval-Augmented Generation over a company knowledge base to ground answers with citations.
  - V004 (Deep Planning): Planner-driven research that asks clarifying questions, orchestrates RAG/Search, and synthesizes a cited answer.
  - Evaluation: LLM-as-judge rubric + basic groundedness checks; experiment tracking via MLflow.

## 2. Scope
- In-scope:
  - CLI experience
  - Agent implementation with Google ADK
  - Search tool integration (V002)
  - Retrieval-Augmented Generation (V003)
  - Deep planning and clarification dialog (V004)
  - Evaluation harness and reporting
  - Experiment tracking (MLflow)
- Out-of-scope:
  - Web UI
  - Large-scale web crawling/scraping; third-party paywalled sources
  - Production multi-tenant deployment

## 3. Phased Delivery
### V001 (MVP)
- Interface: Console app prompts for target company and question.
- Backend: Single model call, deterministic temperature by default.
- Output: Direct answer.

### V002 (POC)
- Interface: Same console app.
- Backend: Agent uses Search tool to gather evidence, performs multi-step reasoning (deep research), and composes a grounded answer with citations.
- Output: Answer + references to sources.

### V003 (RAG)
- Interface: Same console app with additional RAG controls.
- Backend: Retrieval-Augmented Generation over a company knowledge base (vector store) with optional fallback to V002 Search when recall is low.
- Output: Answer grounded primarily on retrieved context with inline citations to stored sources; indicates when no relevant context found.
- Additional capabilities:
  - Ingestion pipeline to index company documents (PDF, HTML, Markdown, TXT, CSV summaries) into a vector store.
  - Configurable chunking and embedding models; retriever with top_k/MMR/hybrid options.

### V004 (Deep Planning + Clarification)
- Interface: Interactive dialog capable of asking the user targeted clarifying questions when necessary; supports a non-interactive mode with assumption policies.
- Backend: A planner that decomposes the task, decides which information to collect (RAG vs. web search vs. ask user), sequences/parallelizes actions, and synthesizes a final answer.
- Output: Answer with citations, explicit list of assumptions (if any), and a brief plan summary.

## 4. User Stories
- As a user, I can ask questions about a company and get an answer (V001).
- As a user, I can see references to sources used in the answer (V002).
- As an evaluator, I can run a batch over an evaluation dataset and get metrics and a report.

### V003 (RAG)
- End user
  - As a user, I want answers grounded in my company knowledge base with citations, so that I can trust and verify responses.
  - As a user, I want a “RAG-only” mode, so that answers come exclusively from approved sources.
  - As a user, I want sources labeled as “RAG” vs “Web,” so that I can judge trustworthiness.
  - As a user, I want to select the company and index version, so that I query the correct snapshot.
  - As a user, I want to see short snippets and links/file paths of cited chunks, so that I can inspect context quickly.
  - As a user, I want the agent to say when no relevant KB context exists and optionally fall back to web search, so that I’m aware of limitations.

- Operator/Admin
  - As an operator, I want to ingest/update/delete company documents and reindex incrementally, so that the KB stays fresh with minimal downtime.
  - As an operator, I want to configure chunking and embedding settings per company, so that retrieval can be tuned per domain.
  - As an operator, I want to version, export, and roll back indexes, so that I can manage deployments safely.
  - As an operator, I want diagnostics on retrieval (hit rate, score distributions), so that I can validate index health.

- Evaluator
  - As an evaluator, I want to run A/B experiments with RAG on/off and with different retriever configs, so that I can quantify RAG’s impact.
  - As an evaluator, I want per-item retrieval logs and citations, so that I can audit grounding and detect unsupported claims.

### V004 (Deep Planning + Clarification)
- End user
  - As a user, I want the agent to ask at most N targeted clarifying questions only when needed, so that ambiguity is resolved without overwhelming me.
  - As a user, I want to set budgets (max steps, max questions) and run non-interactively with an assumptions policy, so that it fits my workflow.
  - As a user, I want to preview a brief plan summary and optionally approve it, so that I know what actions the agent will take.
  - As a user, I want the final answer to list assumptions and residual uncertainties, so that I understand limitations.
  - As a user, I want an “explain plan” option to see a high-level reasoning trace and sources, so that I can audit the process.

- Operator/Admin
  - As an operator, I want to configure planner policies (RAG-first/Search-first/Balanced) and parallelism, so that I can trade off speed vs thoroughness.
  - As an operator, I want to set templates for clarifying question style and quality, so that user experience is consistent.
  - As an operator, I want watchdogs for loop detection and redundancy filters, so that the system avoids over-analysis.
  - As an operator, I want plan traces and task graphs persisted, so that I can debug and improve policies.

- Evaluator
  - As an evaluator, I want to measure human burden (number of questions) and question helpfulness, so that I can assess UX quality.
  - As an evaluator, I want to compare V004 vs V003 on quality vs steps/cost, so that I can quantify planning value.
  - As an evaluator, I want failure mode tagging (unnecessary questions, loops, redundant actions), so that I can target improvements.

## 5. System Architecture (High-level)
- Components:
  - CLI runner
  - Agent (Google ADK)
  - Tools: Search (V002), Retriever (V003), helper formatters
  - RAG store (vector DB) and ingestion pipeline (V003)
  - Planner and Dialogue Manager (V004)
  - Evaluation harness (dataset loader, judge, metrics)
  - MLflow experiment tracker
- Data Flow (V002):
  - User query → Agent → Search tool (N steps with guardrails) → Evidence set → Final answer with citations.
 - Data Flow (V003):
   - User query → Retriever (vector DB) → Context pack → Answer synthesis constrained to context → Citations → If context below threshold, optionally call Search (V002) → Merge or fallback.
 - Data Flow (V004):
   - User query → Planner drafts plan (sub-questions, actions, dependencies) → If missing critical info: ask user clarifying Qs (≤ N) → Execute actions: RAG retrieval and/or Search with budgets → Collect evidence to blackboard → Synthesize answer with citations and assumptions.

## 6. Functional Requirements
### Agent (V001)
- Accepts `company_name` and `question`.
- Calls configured model with a prompt template.
- Returns answer text.

### Agent (V002)
- Orchestrates a “deep research” pattern:
  - Plan: Derive sub-questions.
  - Search: Call Search tool with throttling and retries.
  - Read: Extract key facts from snippets/results.
  - Synthesize: Compose a grounded answer.
  - Cite: Include top K sources with titles/URLs.
- Limits:
  - Max steps: default 8; configurable.
  - Max search calls per query: default 10; configurable.
- Must avoid redundant queries via simple caching (optional but recommended).

### Agent (V003)
- Implements Retrieval-Augmented Generation:
  - Retrieve: Query vector store with `top_k` and similarity threshold; support MMR/hybrid lexical+vector if available.
  - Ground: Prefer answers grounded in retrieved context; do not invent facts beyond context unless explicitly marked as uncertain.
  - Cite: Include citations to ingested source URIs/filenames and chunk ids.
  - Fallback: If `retrieval_hit_rate` < threshold or no context, optionally invoke V002 Search path, then respond; clearly label when no grounded context is available.
- Limits/config:
  - `retriever.top_k` default 8; `retriever.min_score` default 0.3; `retriever.strategy` in {similarity, mmr, hybrid}.
  - `embedding.model` configurable; `chunk.size` and `chunk.overlap` configurable.

### Agent (V004)
- Planning and Execution:
  - Plan: Build a task graph with node types {retrieve_rag, search_web, ask_user, read, synthesize} with dependencies and priorities.
  - Budget: Enforce `max_steps` (default 20), `max_parallel_tasks` (default 2), and `max_user_questions` (default 3).
  - Decision policy: Prefer RAG when retrieval score ≥ threshold; otherwise escalate to Search; only ask user when ambiguity blocks progress.
  - Loop guard: Detect stagnation (no new evidence) and revise plan or stop.
- Clarification Dialog:
  - Select top information gaps using uncertainty scoring; ask concise, specific questions.
  - Non-interactive mode: auto-assume defaults per `--assume-missing` policy and record assumptions.
- Synthesis:
  - Aggregate evidence from blackboard; include citations; enumerate assumptions and residual uncertainties.
  - Produce a short plan summary section in the answer when `--explain-plan` is set.
- Logging:
  - Record plan versions, chosen actions, evidence map, step-by-step trace, and user Q/A pairs.

### Tools
- Search tool:
  - Inputs: query string.
  - Outputs: list of results (title, url, snippet).
  - Reliability: retries with exponential backoff; timeout per call; rate limit ceiling.
- Utilities:
  - URL deduplication
  - Basic snippet scoring
  - Source citation formatter

- Retriever (V003):
  - Inputs: query string, `top_k`, `min_score`.
  - Outputs: list of passages (text, source_uri, chunk_id, score, metadata).
  - Supports MMR/hybrid where available; logs queries and scores for observability.

- Ingestion Pipeline (V003):
 - Planner (V004):
  - Inputs: user goal, constraints (budgets), available tools status.
  - Outputs: task graph (JSON), step selection decisions.
  - Policies: novelty threshold to avoid redundant actions; step watchdog to prevent loops.

 - Dialogue Manager (V004):
  - Decides whether to ask user; formats questions; handles timeouts/non-response with assumptions.
  - Respects `max_user_questions` and non-interactive mode.
  - Inputs: path(s)/URIs to company documents or structured data.
  - Processing: parsing, cleaning, chunking, embedding, indexing.
  - Outputs: populated vector index; manifest with dataset/version metadata.
  - Reliability: resumable ingestion; idempotent updates; reindex flag.

### Evaluation
- Dataset format (JSONL):
  - Fields: `id`, `company`, `question`, `expected_answer` (optional), `references` (optional).
- Judge:
  - LLM-as-judge using a rubric (correctness, groundedness, completeness, citation quality).
  - Scale: 0–1 or {fail, borderline, pass}; plus rationale.
- Metrics:
  - Accuracy/pass rate
  - Average groundedness score
  - Average completeness score
  - Cost per sample, latency
  - V004 metrics:
    - plan_steps_per_item, tool_calls_per_item
    - num_clarifying_questions, human_burden_score
    - redundancy_rate (duplicate queries/actions)
    - efficiency_gain over V003 (quality vs steps)
- Baselines:
  - V001 as baseline for V002 comparison
- Reporting:
  - CSV/JSONL of per-item judgments
  - Aggregate metrics table
  - Top failure modes summary
  - Retrieval diagnostics (hit_rate@k, avg_context_tokens, avg_score)
  
### Experiment Tracking (MLflow)
- Logged params: model name, temperature, max_steps, tool limits, prompt version, dataset id.
- Logged metrics: pass_rate, groundedness, completeness, avg_latency_ms, avg_cost_usd.
- Artifacts: per-item judgments file, answer transcripts, config snapshot.
 - V003 additions:
 - V004 additions:
   - Params: planner.max_steps, planner.max_parallel_tasks, planner.policy, max_user_questions, assume_missing_policy, explain_plan.
   - Metrics: num_steps, num_questions, num_tool_calls, plan_revisions, redundancy_rate, efficiency_gain.
   - Artifacts: final plan JSON, step trace, plan visualization (e.g., Mermaid), dialog transcript.
   - Params: embedding.model, chunk.size, chunk.overlap, retriever.top_k, retriever.min_score, retriever.strategy, index.backend, index.version.
   - Metrics: retrieval_hit_rate_at_k, mean_retrieval_score, context_coverage (percent of answer tokens supported by context), faithfulness score.
   - Artifacts: index manifest, ingestion logs, sampled retrieved contexts.

## 7. Non-Functional Requirements
- Latency: p95 ≤ 15s (V001), ≤ 30s (V002), ≤ 30s (V003) under default limits.
 - Interactivity (V004): interactive prompts should appear within 3s; total run p95 ≤ 60s with defaults.
- Cost: configurable budget cap per run; abort if exceeded.
- Reproducibility: seed, prompt versioning, tool configs logged.
- Observability: structured logs; spans for tool calls; error logs with correlation id.
 - Storage: vector index size tracked; target < 2 GB for demo datasets; support pruning/compaction.

## 8. Configuration and Environments
- Envs: `GOOGLE_API_KEY`, search API creds (if used), `MLFLOW_TRACKING_URI`.
- V003 envs:
  - `RAG_INDEX_BACKEND` in {faiss, chroma, sqlite, other}
  - `RAG_INDEX_DIR` (for local index persistence)
  - `EMBEDDING_MODEL` (e.g., `text-embedding-004` or alternative)
  - Optional cloud vector DB creds if using managed services
- Profiles: `dev`, `test`, `prod` via env vars or config files.
- CLI flags override env/config.

## 9. Prompting & Model Settings
- Defaults: `model`, `temperature`, `top_p`, `max_output_tokens`.
- Prompt templates versioned; include instruction for citations and groundedness.
- Safety: disable chain-of-thought logging externally; request final answers + short justifications.
 - V003 prompting: constrain answers to retrieved context; when context is insufficient, either abstain or clearly label uncertainty; include citations `[n]` mapping to retrieved sources.
 - V004 prompting: separate prompts for planner vs synthesizer; planner prompt forbids revealing chain-of-thought externally and outputs structured plan JSON; synthesizer prompt composes final answer with citations and optional plan summary.

## 10. Tooling & Orchestration
- Timeouts and retries for each tool call (retry up to 3, backoff jitter).
- Rate limiting: global and per-tool ceilings.
- Caching: in-memory per-run cache for identical queries (optional).
- Failure Handling: fallback to fewer steps; graceful degradation to V001 answer if tools fail.
 - V003 orchestration: retrieval first; if below `min_score` or empty, optionally call Search (V002) and merge contexts with deduplication.
 - V004 orchestration: action scheduler supports limited parallelism; novelty filter to prevent repeated queries; loop detector triggers plan revision or early stop; human-in-the-loop gate for clarification.

## 11. Data & Storage
- Local artifacts dir per run (answers, evidence, logs, judgments).
- No PII storage; redact sensitive content in logs.
 - V003 data:
  - V004 data:
    - Blackboard/evidence store schema: `evidence_id`, `type` (rag|web|user), `text`, `source_uri`, `score`, `timestamp`, `provenance`.
    - Plan trace files stored as JSONL per run for auditing and analysis.
   - Supported inputs: PDF, HTML, Markdown, TXT, CSV summaries.
   - Chunking: default size 800 tokens, overlap 150; configurable per ingestion.
   - Metadata schema: `company`, `source_uri`, `doc_id`, `chunk_id`, `created_at`, `version`.
   - Index versioning: maintain `index.version` and manifest for reproducibility.

## 12. Observability & Logging
- Structured JSON logs with timestamps, run_id, sample_id.
- Levels: info for steps, warning for recoverable issues, error for aborts.
- Optional pretty console output for CLI.
 - V003 logs: retrieval queries, top_k, scores, selected chunks, thresholds applied.
  - V004 logs: plan JSON, selected actions, loop detection events, user questions and responses, per-step timings.

## 13. Error Handling & Reliability
- Categories: tool timeout, empty results, quota exceeded, malformed responses.
- Policies: retry strategy; clear user-facing message on abort; record failure in report.
 - V003 specifics: handle empty/low-score retrieval, index-missing errors, ingestion parse failures; provide `--reindex` recovery path.
  - V004 specifics: detect plan stalls; cap user question loops; degrade to V003/V002 with clear note; abort with actionable message when budgets/limits exceeded.

## 14. Security & Privacy
- API keys via env vars; never commit.
- Respect robots/ToS for search.
- Avoid storing full-page contents; only store short snippets and URLs.
 - RAG ingestion: ensure licensing compliance of stored documents; allow redaction and deletion by `doc_id`.
  - Dialogue: avoid collecting sensitive user data; mask any collected PII in logs.

## 15. Testing Strategy
- Unit: tools and formatters.
- Integration: agent + tool with mocked responses.
- Golden tests: prompt snapshots vs. expected outputs.
- Evaluation tests: small fixed dataset to validate scoring pipeline.
 - V003 tests:
  - V004 tests:
    - Planner unit tests with synthetic tasks to validate task graph structure and budget enforcement.
    - Dialogue policy tests to ensure `max_user_questions` respected and assumption policy applied.
    - End-to-end deep planning run with mocked tools to verify loop detection and plan revision.
   - Retrieval unit tests with synthetic corpus; verify top_k and score thresholds.
   - Ingestion tests for chunking and metadata integrity.
   - End-to-end RAG answering with fixed index; golden comparisons of citations.

## 16. Run Modes & CLI
- Interactive:
  - `python -m app --model <model> --company "<name>" --question "<q>"`
- Batch evaluation:
  - `python -m app --eval --dataset <path> --model <model> --steps 8 --mlflow --run-name "<label>"`
- Dry-run and verbose flags.
 - V003 RAG operations:
  - V004 deep planning:
    - Plan & run interactively: `python -m app --deep --company "<name>" --question "<q>" --max-steps 20 --max-questions 3 --explain-plan`
    - Non-interactive with assumptions: `python -m app --deep --non-interactive --assume-missing conservative --company "<name>" --question "<q>"`
    - Evaluate V004: `python -m app --eval --deep --dataset <path> --mlflow --run-name "v004_<label>"`
   - Ingest: `python -m app --ingest --source-dir <path> --company "<name>" --chunk-size 800 --chunk-overlap 150 --index-version v1`
   - Query with RAG: `python -m app --rag --retriever.top_k 8 --retriever.min_score 0.3 --company "<name>" --question "<q>"`
   - Evaluate with RAG: `python -m app --eval --rag --dataset <path> --retriever.top_k 8 --mlflow --run-name "v003_<label>"`

## 17. Baselines & Comparisons
 - Report diffs V001 vs V002 vs V003 vs V004 per metric.
- Keep best-of-N experiment tracking with tags.
 - Ablations: V003 without RAG (off) vs with RAG (on); different `top_k` and embedding models.
 - V004 ablations: planner on/off; with vs without clarifying questions; varying `max_steps` and `max_questions`.

## 18. Risks & Mitigations
- Quotas/outages: exponential backoff, configurable ceilings, resume-able batch.
- Non-determinism: seed where supported, track prompts and configs.
- Hallucinations: enforce citation requirement; judge groundedness; penalize uncited claims.
 - Index freshness: schedule periodic re-ingestion or manual triggers; store source timestamps.
 - Embedding drift: pin embedding model versions; reindex when models change significantly.
 - Data licensing: restrict ingestion to allowed sources; maintain provenance metadata.
  - Planner loops/over-analysis: watchdog timers, step budgets, novelty thresholds, early stopping; cap user questions to reduce fatigue.
  - Ineffective questions: heuristic scoring and A/B templates; revert to default plan if questions do not reduce uncertainty.

## 19. Acceptance Criteria
- V001: answers interactive questions; passes smoke tests; MLflow logs basic run.
- V002: produces answers with ≥ 80% citation presence and ≥ baseline pass rate; batch evaluation and report working.
 - V003: achieves ≥ 0.6 retrieval hit_rate@k on evaluation set, ≥ V002 pass rate (or +5% relative), and ≥ 90% answers include at least one RAG citation when context exists.
 - V004: achieves ≥ V003 pass rate (or +5% relative) while using ≤ 3 clarifying questions per item (p95); redundancy_rate ≤ 10%; average steps ≤ 20 under default budgets; produces explicit assumptions section when applicable.

## 20. Open Questions
- Which search provider and quotas?
- Minimum citation count K?
- Dataset size and provenance?
 - Vector DB backend preference (faiss/chroma/managed)?
 - Embedding model choice and tokenization constraints?
 - Hybrid retrieval (BM25 + vectors) needed?
 - Best heuristic for question selection and when to ask vs search?
 - Should planner output be persisted for reuse across similar queries?
 - How to visualize plan succinctly for reports (Mermaid vs. textual)?