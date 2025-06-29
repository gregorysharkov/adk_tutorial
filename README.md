# Google ADK Tutorial

This project demonstrates the setup and basic usage of Google ADK (Agent Development Kit) in a Poetry environment with Python 3.13+.

## Official Documentation

- **Google ADK Documentation**: https://ai.google.dev/docs/adk
- **Google ADK Python SDK**: https://ai.google.dev/docs/adk/python
- **Google ADK Quickstart**: https://ai.google.dev/docs/adk/quickstart
- **Google ADK API Reference**: https://ai.google.dev/docs/adk/reference
- **Google ADK Examples**: https://ai.google.dev/docs/adk/examples
- **Google AI Studio**: https://makersuite.google.com/app/apikey

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
├── pyproject.toml          # Poetry configuration
├── test_adk.py            # Test script to verify installation
├── example.py             # Basic usage example
├── setup_google_adk.py    # Setup script for API key configuration
├── test_auth.py           # Authentication test script
├── .env                   # Environment variables (API keys)
└── README.md              # This file
```

## Usage

### Test Installation
```bash
poetry run python test_adk.py
```

### Run Example
```bash
poetry run python example.py
```

### Setup Authentication
```bash
poetry run python setup_google_adk.py
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

- **Main Documentation**: https://ai.google.dev/docs/adk
- **Python SDK**: https://ai.google.dev/docs/adk/python
- **API Reference**: https://ai.google.dev/docs/adk/reference
- **Examples**: https://ai.google.dev/docs/adk/examples 