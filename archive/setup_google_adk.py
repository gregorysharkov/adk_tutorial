#!/usr/bin/env python3
"""
Setup Google ADK with API Key (not Vertex AI)
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def setup_google_adk():
    print("🚀 Setting up Google ADK with API Key")
    print("=" * 40)

    # Get API key from environment
    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        print("❌ GOOGLE_API_KEY not found in environment!")
        print("Please add GOOGLE_API_KEY=your_key to your .env file")
        return False

    try:
        # Configure Google GenAI
        try:
            import google.generativeai as genai

            genai.configure(api_key=api_key)
            print("✅ Google GenAI configured with API key")
        except ImportError:
            print("❌ Google GenAI module not found!")
            print("🔧 To fix this, run:")
            print("   poetry add google-generativeai")
            return False

        # Import Google ADK
        from google import adk

        print("✅ Google ADK imported successfully")

        # Set environment variable to disable Vertex AI
        os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "False"
        print("✅ Disabled Vertex AI usage")

        return True

    except Exception as e:
        print(f"❌ Setup failed: {e}")
        return False


def test_basic_functionality():
    print("\n🧪 Testing Basic Functionality")
    print("=" * 40)

    try:
        from google import adk
        from google.adk import models, agents, tools

        print("✅ All Google ADK modules imported successfully")
        print("✅ Ready to use Google ADK with API key!")

        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def install_missing_packages():
    print("\n📦 Installing Missing Packages")
    print("=" * 40)

    print("🔧 Run these commands to install missing packages:")
    print("   poetry add google-generativeai")
    print("   poetry install")
    print("\nThen run this script again.")


if __name__ == "__main__":
    if setup_google_adk():
        test_basic_functionality()
    else:
        install_missing_packages()
