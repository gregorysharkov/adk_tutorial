# Configuration System

This directory contains configuration files for the ADK tutorial system.

## Evaluation Configuration

The evaluation system now uses YAML-based configuration files instead of CLI arguments, making it much easier to manage different evaluation scenarios.

### Base Configuration

**`evaluation.yaml`** - Base evaluation configuration with all available settings:

```yaml
# Agent configuration for evaluation
agent:
  version: "v001"
  model: "gemini-1.5-pro-latest"
  temperature: 0.2
  max_output_tokens: 1024

# LLM-as-Judge configuration
judge:
  enabled: true
  model: "gemini-1.5-pro-latest"
  temperature: 0.0  # Low temperature for factual judging

# Dataset configuration
datasets:
  use_combined: true  # Use both original + transformed datasets
  original: "data/datasets/company_qa_eval_100.jsonl"
  transformed: "data/datasets/transformed_companies_qa.jsonl"
  custom: null  # Override with custom dataset

# MLflow configuration
mlflow:
  enabled: true
  experiment: "adk_tutorial_eval"
  run_name: ""  # Auto-generated if empty
```

### Evaluation Profiles

**`evaluation_profiles/`** - Pre-configured evaluation scenarios:

#### Quick Profile (`quick.yaml`)
- Fast evaluation for testing
- Disabled judge and MLflow
- Uses small test dataset
- Fewer workers for speed

#### Full with Judge (`full_with_judge.yaml`)
- Comprehensive evaluation
- LLM-as-judge enabled
- Both datasets combined
- Full MLflow logging

### Usage

#### 1. Use Default Configuration
```bash
# Uses evaluation.yaml with default settings
poetry run adk --eval-combined
```

#### 2. Use Pre-configured Profile
```bash
# Quick evaluation for testing
poetry run adk --eval-profile quick

# Full evaluation with judge
poetry run adk --eval-profile full_with_judge
```

#### 3. Override Profile Settings
```bash
# Use profile but override specific settings
poetry run adk --eval-profile full_with_judge \
  --judge-enabled \
  --judge-model "gemini-1.5-flash" \
  --run-name "custom-run-name"
```

#### 4. Legacy CLI Mode (Still Supported)
```bash
# Single dataset evaluation
poetry run adk --eval --dataset "path/to/dataset.jsonl"

# Combined datasets with manual judge config
poetry run adk --eval-combined --judge-enabled
```

### Creating Custom Profiles

1. Create a new YAML file in `evaluation_profiles/`
2. Use `_extends: "../evaluation.yaml"` to inherit base settings
3. Override only the settings you want to change

Example:
```yaml
# evaluation_profiles/my_custom.yaml
_extends: "../evaluation.yaml"

agent:
  version: "v002"  # Override agent version

judge:
  enabled: false  # Disable judge for this profile

datasets:
  use_combined: false
  custom: "data/datasets/my_custom_dataset.jsonl"

mlflow:
  run_name: "my-custom-eval"
```

### Configuration Hierarchy

1. **Base config** (`evaluation.yaml`) - Default values
2. **Profile config** (e.g., `quick.yaml`) - Overrides base
3. **CLI overrides** - Final overrides via `--judge-enabled`, `--run-name`, etc.

### Key Benefits

- **No more Python code**: Just use CLI commands
- **Reusable profiles**: Share evaluation configurations
- **Easy customization**: Modify YAML files instead of CLI arguments
- **Version control**: Track evaluation configurations in git
- **Team collaboration**: Standardized evaluation setups
