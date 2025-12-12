#!/bin/bash

# Streamlit Trading App Installation Script

echo "🔧 Installing Streamlit Trading App with compatible dependencies..."

# Upgrade pip
python -m pip install --upgrade pip

# Install compatible versions
pip install "streamlit==1.28.1" "rich<14,>=10.14.0" "markdown-it-py>=2.2.0" "mdurl==0.1" "pygments<3.0.0,>=2.13.0"

# Optional dependencies
read -p "Install optional dependencies? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    pip install openai pillow
    echo "✅ Optional dependencies installed"
fi

# Verify installation
echo "✅ Installation complete!"
echo "Run: streamlit run app.py"
