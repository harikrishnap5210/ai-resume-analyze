#!/bin/bash

echo "================================"
echo "  Resume Analyzer - Starting"
echo "================================"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found"
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo ""
    echo "❗ IMPORTANT: Edit .env and add your GROQ_API_KEY"
    echo "   Then run this script again."
    exit 1
fi

# Load environment variables
export $(cat .env | xargs)

if [ -z "$GROQ_API_KEY" ]; then
    echo "❌ Error: GROQ_API_KEY not set in .env"
    echo "   Please add your Groq API key to .env file"
    exit 1
fi

echo "✅ Environment variables loaded"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt
echo ""

# Start server
echo "🚀 Starting server..."
echo "   Local: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop"
echo ""

uvicorn resumeAnalyzer_groq:app --host 0.0.0.0 --port 8000 --reload
