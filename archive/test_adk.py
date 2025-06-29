#!/usr/bin/env python3
"""
Simple test to verify Google ADK installation
"""

try:
    from google import adk

    print("✅ Google ADK successfully imported!")

    # Get version information
    try:
        from google.adk import version

        print(f"Version: {version.__version__}")
    except:
        print("Version information not available")

    # Test basic functionality
    print("\n🔍 Available modules:")
    for item in dir(adk):
        if not item.startswith("_"):
            print(f"  - {item}")

    # Test some basic imports
    print("\n🧪 Testing basic imports:")
    try:
        from google.adk import agents

        print("  ✅ agents module imported")
    except Exception as e:
        print(f"  ❌ agents module failed: {e}")

    try:
        from google.adk import tools

        print("  ✅ tools module imported")
    except Exception as e:
        print(f"  ❌ tools module failed: {e}")

    try:
        from google.adk import models

        print("  ✅ models module imported")
    except Exception as e:
        print(f"  ❌ models module failed: {e}")

except ImportError as e:
    print(f"❌ Failed to import Google ADK: {e}")
except Exception as e:
    print(f"❌ Error: {e}")

print(f"\n🐍 Python version: {__import__('sys').version}")
