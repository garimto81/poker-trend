#!/bin/bash

# Setup script for YouTube trend analysis
# This script prepares the environment for GitHub Actions execution

echo "Setting up YouTube trend analysis environment..."

# Create necessary directories
echo "Creating directories..."
mkdir -p logs
mkdir -p reports

# Make the Python script executable
chmod +x run_youtube_analysis.py

echo "Setup completed!"