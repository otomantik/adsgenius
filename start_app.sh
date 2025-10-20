#!/bin/bash

echo "========================================"
echo "  Marketing Intelligence Platform"
echo "  Starting Application..."
echo "========================================"
echo ""

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
else
    echo "No virtual environment found. Using system Python..."
fi

echo ""
echo "Starting Streamlit application..."
echo ""
echo "========================================"
echo "  Application will open in your browser"
echo "  Press CTRL+C to stop the server"
echo "========================================"
echo ""

streamlit run streamlit_app.py


