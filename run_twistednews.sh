#!/bin/bash
# TwistedNews execution script

# Set working directory to script location
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "========================================="
echo "  TwistedNews - News Commentary Generator"
echo "========================================="
echo ""

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    echo "Activating virtual environment..."
    source ./.venv/bin/activate
    echo -e "${GREEN}✓ Virtual environment activated${NC}"
    echo ""
elif [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source ./venv/bin/activate
    echo -e "${GREEN}✓ Virtual environment activated${NC}"
    echo ""
else
    echo -e "${YELLOW}⚠ No virtual environment found (.venv or venv)${NC}"
    echo ""
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${RED}Error: .env file not found${NC}"
    echo "Please copy .env.example to .env and configure it"
    exit 1
fi

# Check if TwistedPair is running
echo "Checking TwistedPair server..."
if ! curl -s http://localhost:8001/health > /dev/null 2>&1; then
    echo -e "${RED}Error: TwistedPair server not responding${NC}"
    echo "Please start TwistedPair V2 server:"
    echo "  cd ../TwistedPair/V2"
    echo "  uvicorn server:app --host 0.0.0.0 --port 8001"
    exit 1
fi
echo -e "${GREEN}✓ TwistedPair server is running${NC}"
echo ""

# Run TwistedNews
echo "Running TwistedNews..."
echo ""

python main.py "$@"

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✓ TwistedNews completed successfully${NC}"
else
    echo ""
    echo -e "${RED}✗ TwistedNews failed with exit code $EXIT_CODE${NC}"
fi

exit $EXIT_CODE
