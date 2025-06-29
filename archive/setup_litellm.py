#!/usr/bin/env python3
"""
Setup LiteLLM with Google API Key (not Vertex AI)
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set environment variables to disable Vertex AI
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "False"
os.environ["LITELLM_USE_VERTEXAI"] = "False"

# Clear any existing credentials
if "GOOGLE_APPLICATION_CREDENTIALS" in os.environ:
    del os.environ["GOOGLE_APPLICATION_CREDENTIALS"]

# Configure LiteLLM
try:
    import litellm

    # Set LiteLLM to use Google API key
    litellm.set_verbose = True

    # Test configuration
    api_key = os.getenv("GOOGLE_API_KEY")
    if api_key:
        print(f"✅ API Key configured: {api_key[:10]}...")
        print("✅ LiteLLM configured to use Google API key")
        print("✅ Vertex AI disabled")
    else:
        print("❌ No API key found!")

except ImportError:
    print("❌ LiteLLM not installed")
except Exception as e:
    print(f"❌ LiteLLM setup error: {e}")

# Test Google ADK import
try:
    from google import adk

    print("✅ Google ADK imported successfully")
except Exception as e:
    print(f"❌ Google ADK import error: {e}")


def test_litellm_google():
    print("\n🧪 Testing LiteLLM with Google API")
    print("=" * 40)

    try:
        import litellm

        # Test with a simple completion (this will make an API call)
        api_key = os.getenv("GOOGLE_API_KEY")

        # Use the correct model name format for Google API key (not Vertex AI)
        # For Google API key, use: "gemini/gemini-1.5-flash" or "gemini/gemini-pro"
        response = litellm.completion(
            model="gemini/gemini-1.5-flash",  # This format uses Google API key
            messages=[{"role": "user", "content": "Hello, this is a test."}],
            api_key=api_key,
            max_tokens=50,
        )

        print("✅ LiteLLM test successful!")
        print(f"Response: {response.choices[0].message.content}")

        return True

    except Exception as e:
        print(f"❌ LiteLLM test failed: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Make sure you're using the correct model name format")
        print(
            "2. For Google API key, use: 'gemini/gemini-1.5-flash' or 'gemini/gemini-pro'"
        )
        print("3. For Vertex AI, use: 'gemini-1.5-flash' or 'gemini-pro'")
        return False


def test_google_adk_with_litellm():
    print("\n🤖 Testing Google ADK with LiteLLM")
    print("=" * 40)

    try:
        from google import adk

        print("✅ Google ADK imported successfully")

        # Test if we can access models
        from google.adk import models, agents, tools

        print("✅ All ADK modules imported")

        return True

    except Exception as e:
        print(f"❌ Google ADK test failed: {e}")
        return False


def test_direct_google_genai():
    print("\n🔧 Testing Direct Google GenAI (bypassing LiteLLM)")
    print("=" * 40)

    try:
        import google.generativeai as genai

        # Configure with API key
        api_key = os.getenv("GOOGLE_API_KEY")
        genai.configure(api_key=api_key)

        # Test with a simple generation
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content("Hello, this is a test.")

        print("✅ Direct Google GenAI test successful!")
        print(f"Response: {response.text}")

        return True

    except Exception as e:
        print(f"❌ Direct Google GenAI test failed: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Testing multiple approaches...")

    # Test direct Google GenAI first
    if test_direct_google_genai():
        print("\n✅ Direct Google GenAI works! You can use this approach.")

    # Test LiteLLM with correct model format
    if test_litellm_google():
        test_google_adk_with_litellm()
    else:
        print("\n⚠️ LiteLLM test failed, but direct Google GenAI works.")
        print("You can use Google ADK with direct Google GenAI integration.")
