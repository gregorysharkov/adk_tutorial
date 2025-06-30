#!/bin/bash

# Multi-Agent ADK App Startup Script

echo "🤖 Starting Multi-Agent ADK Application..."
echo "=========================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please create it first:"
    echo "   python3 -m venv venv"
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from template..."
    if [ -f "env_example.txt" ]; then
        cp env_example.txt .env
        echo "📝 Please edit .env file and add your Google API key"
        echo "   Then run this script again"
        exit 1
    else
        echo "❌ env_example.txt not found"
        exit 1
    fi
fi

# Check if API key is set
if grep -q "your_google_api_key_here" .env; then
    echo "❌ Please update your API key in the .env file"
    exit 1
fi

# Install dependencies if needed
echo "📦 Checking dependencies..."
pip install -r requirements.txt

# Run the application
echo "🚀 Starting Streamlit application..."
echo "   The app will open in your browser at http://localhost:8501"
echo "   Press Ctrl+C to stop the application"
echo ""

streamlit run app.py 