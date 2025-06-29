# Google ADK Tutorial

This project demonstrates the setup and basic usage of Google ADK (Agent Development Kit) in a Poetry environment with Python 3.13+.

## Official Documentation

- **Google ADK Documentation**: https://google.github.io/adk-docs/
- **Google ADK Python SDK**: https://google.github.io/adk-docs/get-started/
- **Google ADK Quickstart**: https://google.github.io/adk-docs/get-started/quickstart/
- **Google ADK API Reference**: https://google.github.io/adk-docs/reference/python/
- **Google ADK Examples**: https://github.com/google/adk-samples

## Setup

### Prerequisites
- Python 3.13 or higher
- Poetry (installed automatically during setup)

### Installation

1. **Clone or navigate to this directory**
   ```bash
   cd adk_tutorial
   ```

2. **Install dependencies**
   ```bash
   poetry install
   ```

3. **Activate the virtual environment**
   ```bash
   poetry shell
   ```

## Project Structure

```
adk_tutorial/
├── adk_tutorial/
│   ├── 01_hello_world.ipynb
│   ├── 02_multitool_agent.ipynb
│   ├── 03_agent_team.ipynb
│   ├── agent_call_utils.py
│   └── tools/
│       ├── __init__.py
│       ├── get_greetings.py
│       └── get_weather.py
├── archive/
│   ├── setup_google_adk.py
│   ├── setup_litellm.py
│   ├── simple_google_adk.py
│   ├── test_adk.py
│   └── test_auth.py
├── .gitignore
├── DOCUMENTATION.md
├── example.py
├── poetry.lock
├── pyproject.toml
└── README.md
```

## Usage

### Test Installation
```bash
# No direct test script, run notebooks instead
```

### Run Example
```bash
poetry run jupyter lab
# Then open and run 01_hello_world.ipynb, etc.
```

### Setup Authentication
```bash
# Authentication is handled within the notebooks
```

## Dependencies

- **google-adk**: Google Agent Development Kit (v1.4.2)
- **google-generativeai**: Google Generative AI Python SDK
- **python-dotenv**: Environment variable management
- **Python**: ^3.13

## Key Features

- ✅ Poetry environment management
- ✅ Python 3.13+ support
- ✅ Google ADK integration
- ✅ Google API key authentication
- ✅ Virtual environment isolation
- ✅ Dependency management

## Next Steps

1. **Authentication**: Set up Google API key authentication ✅
2. **Model Configuration**: Configure your preferred AI models
3. **Tool Development**: Create custom tools or use built-in ones
4. **Agent Building**: Develop your AI agents using the ADK

## Useful Commands

```bash
# Add new dependencies
poetry add package-name

# Update dependencies
poetry update

# Show installed packages
poetry show

# Run scripts
poetry run python script.py

# Activate shell
poetry shell

# Start Jupyter
poetry run jupyter lab
```

## Documentation

For the most current and accurate information, always refer to the official Google ADK documentation:

- **Main Documentation**: https://google.github.io/adk-docs/
- **Python SDK**: https://google.github.io/adk-docs/get-started/
- **API Reference**: https://google.github.io/adk-docs/reference/python/
- **Examples**: https://github.com/google/adk-samples 