#!/bin/bash
# Time Revival - Start Script

echo "============================================================"
echo "Time Revival - AI Photo Video Generation System"
echo "============================================================"

# Install dependencies if needed
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

echo "Installing dependencies..."
pip install -r requirements.txt -q

echo ""
echo "Starting server..."
echo ""
python app.py
