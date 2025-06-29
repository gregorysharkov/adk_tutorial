#!/usr/bin/env python3
"""
Simple Google ADK Example - Direct Google GenAI Integration
Bypasses LiteLLM to avoid Vertex AI issues
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure environment
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "False"


def setup_google_genai():
    """Setup Google GenAI with API key"""
    try:
        import google.generativeai as genai

        # Configure with API key
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print("❌ No API key found!")
            return False

        genai.configure(api_key=api_key)
        print(f"✅ Google GenAI configured with API key: {api_key[:10]}...")
        return True

    except Exception as e:
        print(f"❌ Google GenAI setup failed: {e}")
        return False


def test_google_genai():
    """Test Google GenAI directly"""
    try:
        import google.generativeai as genai

        # Test with a simple generation
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content("Say hello in a friendly way!")

        print("✅ Google GenAI test successful!")
        print(f"Response: {response.text}")
        return True

    except Exception as e:
        print(f"❌ Google GenAI test failed: {e}")
        return False


def test_google_adk():
    """Test Google ADK import and basic functionality"""
    try:
        from google import adk
        from google.adk import models, agents, tools

        print("✅ Google ADK imported successfully")
        print("✅ All ADK modules available")

        # List available components
        print("\n📋 Available ADK Components:")
        print(f"  - Models: {len(dir(models))} items")
        print(f"  - Agents: {len(dir(agents))} items")
        print(f"  - Tools: {len(dir(tools))} items")

        return True

    except Exception as e:
        print(f"❌ Google ADK test failed: {e}")
        return False


def main():
    print("🚀 Simple Google ADK Setup (Direct Integration)")
    print("=" * 50)
    print("📚 Documentation: https://ai.google.dev/docs/adk")

    # Setup Google GenAI
    if not setup_google_genai():
        return

    # Test Google GenAI
    if not test_google_genai():
        return

    # Test Google ADK
    if not test_google_adk():
        return

    print("\n✅ All tests passed!")
    print("\n🎯 Next Steps:")
    print("1. ✅ API key authentication (done)")
    print("2. ✅ Google GenAI integration (done)")
    print("3. ✅ Google ADK setup (done)")
    print("4. 🚀 Start building your agents!")

    print("\n📖 Resources:")
    print("  - Quickstart: https://ai.google.dev/docs/adk/quickstart")
    print("  - Examples: https://ai.google.dev/docs/adk/examples")
    print("  - API Reference: https://ai.google.dev/docs/adk/reference")


if __name__ == "__main__":
    main()
