"""
Test script to verify the setup and API connectivity
"""

import os
import sys
from dotenv import load_dotenv
import google.generativeai as genai

def test_environment():
    """Test if environment variables are properly set"""
    print("🔍 Testing environment setup...")
    
    load_dotenv()
    api_key = os.getenv('GOOGLE_API_KEY')
    
    if not api_key:
        print("❌ GOOGLE_API_KEY not found in environment variables")
        print("   Please create a .env file with your API key")
        return False
    
    if api_key == "your_google_api_key_here":
        print("❌ Please replace the placeholder API key with your actual key")
        return False
    
    print("✅ Environment variables loaded successfully")
    return True

def test_api_connection():
    """Test Google Generative AI API connection"""
    print("\n🔍 Testing API connection...")
    
    try:
        genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Simple test prompt
        response = model.generate_content("Hello! Please respond with 'API connection successful' if you can see this message.")
        
        if response.text:
            print("✅ API connection successful")
            print(f"   Response: {response.text}")
            return True
        else:
            print("❌ API returned empty response")
            return False
            
    except Exception as e:
        print(f"❌ API connection failed: {str(e)}")
        return False

def test_dependencies():
    """Test if all required dependencies are installed"""
    print("\n🔍 Testing dependencies...")
    
    required_packages = [
        'streamlit',
        'google.generativeai',
        'dotenv'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package} is installed")
        except ImportError:
            print(f"❌ {package} is missing")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n📦 Install missing packages with:")
        print(f"   pip install {' '.join(missing_packages)}")
        return False
    
    return True

def main():
    """Run all tests"""
    print("🚀 Multi-Agent ADK App - Setup Test")
    print("=" * 50)
    
    tests = [
        test_environment,
        test_dependencies,
        test_api_connection
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with error: {str(e)}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    
    if all(results):
        print("🎉 All tests passed! Your setup is ready.")
        print("\n🚀 To run the application:")
        print("   streamlit run app.py")
    else:
        print("⚠️  Some tests failed. Please fix the issues above.")
        print("\n📖 Check the README.md for setup instructions.")

if __name__ == "__main__":
    main() 