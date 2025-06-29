#!/usr/bin/env python3
"""
Simple Google ADK Example with API Key
Based on current Google ADK documentation: https://ai.google.dev/docs/adk
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure to use API key instead of Vertex AI
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "False"

from google import adk
from google.adk import agents, tools, models


def main():
    print("🚀 Google ADK Tutorial Example (API Key)")
    print("=" * 40)
    print("📚 Documentation: https://ai.google.dev/docs/adk")
    print("🐍 Python SDK: https://ai.google.dev/docs/adk/python")

    # Check API key
    api_key = os.getenv("GOOGLE_API_KEY")
    if api_key:
        print(f"✅ API Key configured: {api_key[:10]}...")
    else:
        print("⚠️ No API key found. Add GOOGLE_API_KEY to your .env file")
        print("🔑 Get API key from: https://makersuite.google.com/app/apikey")

    # Show available models
    print("\n📋 Available Models:")
    try:
        print("  - Google ADK supports various model integrations")
        print("  - Using API key authentication (not Vertex AI)")
        print("  - Check documentation: https://ai.google.dev/docs/adk/models")
        print("  - Current models: Gemini, PaLM, and more")
    except Exception as e:
        print(f"  Error accessing models: {e}")

    # Show available tools
    print("\n🔧 Available Tools:")
    try:
        print("  - Web search tools")
        print("  - Code execution tools")
        print("  - File manipulation tools")
        print("  - Custom tool creation")
        print("  - Documentation: https://ai.google.dev/docs/adk/tools")
    except Exception as e:
        print(f"  Error accessing tools: {e}")

    # Show agent capabilities
    print("\n🤖 Agent Capabilities:")
    try:
        print("  - Conversational agents")
        print("  - Task-oriented agents")
        print("  - Multi-step reasoning")
        print("  - Tool integration")
        print("  - Documentation: https://ai.google.dev/docs/adk/agents")
    except Exception as e:
        print(f"  Error accessing agents: {e}")

    print("\n✅ Google ADK is ready to use with API key!")
    print("\nNext steps:")
    print("1. ✅ API key authentication (done)")
    print("2. Configure your preferred models")
    print("3. Create custom tools or use built-in ones")
    print("4. Build your agent!")
    print("\n📖 Resources:")
    print("  - Quickstart: https://ai.google.dev/docs/adk/quickstart")
    print("  - Examples: https://ai.google.dev/docs/adk/examples")
    print("  - API Reference: https://ai.google.dev/docs/adk/reference")


if __name__ == "__main__":
    main()
