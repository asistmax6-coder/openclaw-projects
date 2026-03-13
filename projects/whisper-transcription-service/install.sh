#!/bin/bash
set -e

echo "🎤 Installing Whisper Transcription Service..."

# Check Python 3.8+
PYTHON_VERSION=$(python3 --version 2>/dev/null | cut -d' ' -f2 | cut -d'.' -f1,2)
if [[ $(echo "$PYTHON_VERSION >= 3.8" | bc) -eq 0 ]]; then
    echo "❌ Python 3.8+ required. Found: $PYTHON_VERSION"
    exit 1
fi

# Check ffmpeg for audio processing
if ! command -v ffmpeg &> /dev/null; then
    echo "📦 Installing ffmpeg for audio format support..."
    if command -v apt-get &> /dev/null; then
        sudo apt-get update && sudo apt-get install -y ffmpeg
    elif command -v brew &> /dev/null; then
        brew install ffmpeg
    elif command -v yum &> /dev/null; then
        sudo yum install -y ffmpeg
    else
        echo "⚠️  Install ffmpeg manually: https://ffmpeg.org/download.html"
    fi
fi

# Create virtual environment
echo "🔧 Setting up virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "📥 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Make scripts executable
chmod +x transcribe.py web_service.py
echo "Create symbolic links..."
ln -sf venv/bin/whisper-transcribe venv/bin/transcribe 2>/dev/null || true

# Copy environment file
test -f .env || cp .env.example .env

echo "✅ Installation complete!"
echo ""
echo "🔑 Next steps:"
echo "1. Set your OpenAI API key: export OPENAI_API_KEY='your-key-here'"
echo "2. Test the CLI: ./transcribe.py sample.ogg"
echo "3. Start web service: ./web_service.py"
echo ""
echo "📖 See README.md for complete usage instructions"