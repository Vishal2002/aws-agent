#!/bin/bash
set -e

echo "=" | tr '=' '=' | head -c 60 >&2
echo "" >&2
echo "🚀 AWS DEPLOYMENT AGENT - STARTUP" >&2
echo "=" | tr '=' '=' | head -c 60 >&2
echo "" >&2

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo "📁 Project directory: $SCRIPT_DIR" >&2

# Change to project directory
cd "$SCRIPT_DIR"

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!" >&2
    echo "   Run: python -m venv venv" >&2
    exit 1
fi

echo "✅ Virtual environment found" >&2

# Activate virtual environment
source venv/bin/activate
echo "✅ Virtual environment activated" >&2

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found!" >&2
    echo "   AWS credentials may not be loaded" >&2
else
    echo "✅ Found .env file" >&2
    # Load environment variables from .env
    export $(cat .env | grep -v '^#' | xargs)
    echo "✅ Environment variables loaded" >&2
fi

# Verify AWS credentials
if [ -z "$AWS_ACCESS_KEY_ID" ]; then
    echo "❌ AWS_ACCESS_KEY_ID not set!" >&2
    exit 1
fi

echo "✅ AWS credentials loaded" >&2
echo "" >&2
echo "🎯 Starting MCP server..." >&2
echo "" >&2

# Start the MCP server
exec python -m mcp_server.server