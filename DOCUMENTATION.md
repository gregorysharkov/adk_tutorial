# Google ADK Documentation Reference

This file contains links to the official Google ADK documentation for reference during development.

## Official Documentation Links

### Main Documentation
- **Google ADK Home**: https://ai.google.dev/docs/adk
- **Google ADK Python SDK**: https://ai.google.dev/docs/adk/python
- **Google ADK Quickstart**: https://ai.google.dev/docs/adk/quickstart

### API and Reference
- **Google ADK API Reference**: https://ai.google.dev/docs/adk/reference
- **Google ADK Python API**: https://ai.google.dev/docs/adk/python/reference
- **Google ADK Models**: https://ai.google.dev/docs/adk/models

### Examples and Tutorials
- **Google ADK Examples**: https://ai.google.dev/docs/adk/examples
- **Google ADK Tutorials**: https://ai.google.dev/docs/adk/tutorials
- **Google ADK Sample Code**: https://github.com/google/adk-python

### Authentication and Setup
- **Google AI Studio**: https://makersuite.google.com/app/apikey
- **Google Cloud Console**: https://console.cloud.google.com/
- **Google Cloud Authentication**: https://cloud.google.com/docs/authentication

### Related Documentation
- **Google Generative AI**: https://ai.google.dev/docs/generative-ai
- **Google AI Studio**: https://makersuite.google.com/
- **Google Cloud AI**: https://cloud.google.com/ai

## Current Version Information

- **Google ADK Version**: 1.4.2 (as of current setup)
- **Python SDK**: Latest version from PyPI
- **Documentation Last Updated**: Check official docs for most current info

## Key Concepts

### What is Google ADK?
Google ADK (Agent Development Kit) is a framework for building AI agents that can:
- Use tools and APIs
- Reason about tasks
- Execute multi-step workflows
- Integrate with various AI models

### Core Components
- **Agents**: The main AI entities that can perform tasks
- **Tools**: Functions that agents can call to interact with external systems
- **Models**: AI models that power the agents' reasoning and responses
- **Sessions**: Context management for agent conversations

### Authentication Methods
1. **API Key**: For Google Generative AI models
2. **Service Account**: For Google Cloud services
3. **Application Default Credentials**: For Google Cloud SDK

## Development Workflow

1. **Setup**: Install Google ADK and configure authentication
2. **Model Selection**: Choose appropriate AI models for your use case
3. **Tool Development**: Create or use existing tools for agent capabilities
4. **Agent Creation**: Build agents that combine models and tools
5. **RAG (V003)**: Ingest company documents into a vector store; configure retriever and prompting
6. **Deep Planning (V004)**: Configure planner and dialogue manager; define budgets and policies
7. **Testing**: Test agents with various scenarios
8. **Deployment**: Deploy agents for production use

## Best Practices

- Always refer to the official documentation for the most current information
- Use environment variables for sensitive configuration
- Test with different models to find the best fit for your use case
- Implement proper error handling for tool calls
- Monitor agent performance and usage
 - For RAG, pin embedding model versions and log index versions

## Setup Checklist

- Install dependencies (see `requirements.txt` / `pyproject.toml`).
- Set environment variables: `GOOGLE_API_KEY`, optional search API creds, `MLFLOW_TRACKING_URI`.
- For V003 (RAG): set `RAG_INDEX_BACKEND`, `RAG_INDEX_DIR`, `EMBEDDING_MODEL`.
- Verify CLI: run V001 interactive, V002 with search, V003 with `--rag`.

## Running Modes (Examples)

- V001 interactive:
  - `python -m app --model <model> --company "<name>" --question "<q>"`
- V002 search-enabled:
  - `python -m app --model <model> --company "<name>" --question "<q>" --steps 8`
- V003 RAG ingestion:
  - `python -m app --ingest --source-dir ./data/<company>/ --company "<name>" --chunk-size 800 --chunk-overlap 150 --index-version v1`
- V003 RAG query:
  - `python -m app --rag --retriever.top_k 8 --retriever.min_score 0.3 --company "<name>" --question "<q>"`
- Batch evaluation (any version):
  - `python -m app --eval --dataset ./datasets/eval.jsonl --mlflow --run-name "exp_label" [--rag]`

- V004 deep planning (interactive):
  - `python -m app --deep --company "<name>" --question "<q>" --max-steps 20 --max-questions 3 --explain-plan`
- V004 deep planning (non-interactive):
  - `python -m app --deep --non-interactive --assume-missing conservative --company "<name>" --question "<q>"`

## Troubleshooting

- Auth errors: confirm `GOOGLE_API_KEY` and ADK version; re-login if using ADC.
- Empty search results: check quotas; reduce steps; verify network.
- RAG retrieval returns no context: ensure index exists in `RAG_INDEX_DIR`; re-run ingestion; lower `retriever.min_score`.
- High latency: lower `top_k`, reduce steps, or raise timeouts.
- Planner asks too many/poor questions: reduce `--max-questions`, switch `--assume-missing` policy to conservative, or run non-interactive mode; review plan trace.

## Changelog

- Added V003: Retrieval-Augmented Generation with ingestion and retriever configuration.
 - Added V004: Deep planning with clarification dialog, planner budgets, and plan visualization.

## Repository Structure

This repository is organized to support multiple agent versions (V001–V004), shared tooling, evaluation, and artifacts.

```
app/
  cli.py                 # Single CLI entrypoint for run/eval/ingest/deep
  agents/                # Agent implementations per version
  config/                # Layered YAML configs: defaults + version + profiles
  prompts/               # Versioned agent/planner/judge prompts
  tools/                 # Search, retriever, ingestion utilities
  orchestration/         # Planner, dialogue, executor, blackboard (V004)
  retrieval/             # Backends, chunking, embeddings, manifests (V003)
  evaluation/            # Datasets, judges, metrics, runner, reporting
  logging/               # Logging setup for structured logs
data/
  sources/               # Raw company docs (local only; respect licensing)
  indexes/               # Vector indexes by company/version (gitignored)
artifacts/
  runs/                  # Run outputs (answers, contexts, judgments)
```

- See `ARCHITECTURE.md` for component diagrams and data flows.
- For migrating from `brisk/`, mirror functionality into `app/` components.

## Architecture Reference

- High-level architecture and flows for V002 (Search), V003 (RAG), V004 (Deep Planning) are documented in `ARCHITECTURE.md`.

## Support and Community

- **GitHub Issues**: https://github.com/google/adk-python/issues
- **Google AI Community**: https://ai.google.dev/community
- **Stack Overflow**: Tag questions with `google-adk` 