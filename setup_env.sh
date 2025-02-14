#!/bin/bash

# Create a virtual environment named 'venv'
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Upgrade pip to the latest version
pip install --upgrade pip

# Install the required packages
pip install pytesseract opencv-python openai

echo "Setup complete. Virtual environment 'venv' is ready with the required packages installed."
