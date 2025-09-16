#!/bin/bash

# Exit on any error
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Running backend tests...${NC}"

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo -e "${RED}Error: pyproject.toml not found. Please run this script from the Backend directory.${NC}"
    exit 1
fi

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo -e "${RED}Error: uv is not installed. Please install uv first.${NC}"
    exit 1
fi

# Install test dependencies using uv
echo -e "${YELLOW}Installing test dependencies with uv...${NC}"
uv sync --all-extras

# Run tests with TESTING environment variable set
echo -e "${YELLOW}Executing tests...${NC}"
TESTING=1 uv run pytest --tb=no -v tests/

echo -e "${GREEN}Tests completed successfully!${NC}"