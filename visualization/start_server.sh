#!/bin/bash

# Quick start script for the visualization server
# This will start a local HTTP server and open the visualization in your browser

echo "🚀 Starting Heterogeneous Graph Visualization Server"
echo "===================================================="
echo ""

# Check if graph_data.json exists
if [ ! -f "graph_data.json" ]; then
    echo "⚠️  Warning: graph_data.json not found!"
    echo "   Using sample data instead..."
    
    if [ ! -f "graph_data_sample_small.json" ]; then
        echo "   Generating sample data..."
        python3 generate_sample_data.py
    fi
fi

echo ""
echo "📊 Server will be available at: http://localhost:8000"
echo ""
echo "💡 Tips:"
echo "   - Press Ctrl+C to stop the server"
echo "   - The visualization will open automatically in your browser"
echo "   - If it doesn't, navigate to http://localhost:8000 manually"
echo ""
echo "===================================================="
echo ""

# Try to open in browser (works on macOS)
sleep 2 && open http://localhost:8000 &

# Start the server
echo "Starting HTTP server..."
python3 -m http.server 8000

