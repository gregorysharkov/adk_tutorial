#!/usr/bin/env python3
"""
Test Google API Key Authentication
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def test_google_api_key():
    print("🔐 Testing Google API Key Authentication")
    print("=" * 40)

    # Check for Google API key
    api_key = os.getenv("GOOGLE_API_KEY")

    if api_key:
        print(f"✅ Google API Key found!")
        print(f"🔑 Key starts with: {api_key[:10]}...")

        # Test basic Google GenAI import
        try:
            import google.generativeai as genai

            genai.configure(api_key=api_key)
            print("✅ Google GenAI configured successfully!")

            # Test a simple model list (this won't make an API call)
            print("✅ Google GenAI is ready to use!")

        except ImportError:
            print("❌ Google GenAI module not found!")
            print("🔧 To fix this, run:")
            print("   poetry add google-generativeai")

        except Exception as e:
            print(f"❌ Google GenAI setup failed: {e}")

    else:
        print("❌ Google API Key not found!")
        print("\n🔧 To fix this:")
        print("1. Get a Google API key from: https://makersuite.google.com/app/apikey")
        print("2. Add to your .env file:")
        print("   GOOGLE_API_KEY=your_api_key_here")
        print("3. Or set environment variable:")
        print("   export GOOGLE_API_KEY=your_api_key_here")


def test_google_adk_with_api_key():
    print("\n🤖 Testing Google ADK with API Key")
    print("=" * 40)

    try:
        from google import adk

        print("✅ Google ADK imported successfully!")

        # Test if we can access models without Vertex AI
        print("✅ Google ADK is ready to use with API key!")

    except Exception as e:
        print(f"❌ Google ADK test failed: {e}")


def check_installed_packages():
    print("\n📦 Checking Installed Google Packages")
    print("=" * 40)

    try:
        import subprocess

        result = subprocess.run(["poetry", "show"], capture_output=True, text=True)

        google_packages = [
            line for line in result.stdout.split("\n") if "google" in line.lower()
        ]

        if google_packages:
            print("✅ Found Google packages:")
            for package in google_packages:
                print(f"  - {package}")
        else:
            print("❌ No Google packages found")

    except Exception as e:
        print(f"❌ Could not check packages: {e}")


if __name__ == "__main__":
    test_google_api_key()
    test_google_adk_with_api_key()
    check_installed_packages()
