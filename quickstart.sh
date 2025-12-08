#!/bin/bash
# Quick Start Script for HPC Matrix Operations System
# This script automates the setup and first run

set -e  # Exit on error

echo "=========================================="
echo "HPC Matrix Operations - Quick Start"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running on supported system
if [[ "$OSTYPE" != "linux-gnu"* ]] && [[ "$OSTYPE" != "darwin"* ]]; then
    echo -e "${RED}Warning: This script is designed for Linux/macOS${NC}"
fi

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo "[1] Checking prerequisites..."

if ! command_exists mpirun; then
    echo -e "${RED}✗ OpenMPI not found${NC}"
    echo "  Install with: sudo apt-get install openmpi-bin openmpi-common libopenmpi-dev"
    exit 1
else
    echo -e "${GREEN}✓ OpenMPI found${NC}"
fi

if ! command_exists mpic++; then
    echo -e "${RED}✗ MPI C++ compiler not found${NC}"
    echo "  Install with: sudo apt-get install libopenmpi-dev"
    exit 1
else
    echo -e "${GREEN}✓ MPI C++ compiler found${NC}"
fi

if ! command_exists python3; then
    echo -e "${RED}✗ Python 3 not found${NC}"
    exit 1
else
    echo -e "${GREEN}✓ Python 3 found${NC}"
fi

if ! command_exists make; then
    echo -e "${RED}✗ Make not found${NC}"
    echo "  Install with: sudo apt-get install build-essential"
    exit 1
else
    echo -e "${GREEN}✓ Make found${NC}"
fi

echo ""

# Install Python dependencies
echo "[2] Installing Python dependencies..."
if pip3 install -r requirements.txt > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Python dependencies installed${NC}"
else
    echo -e "${YELLOW}⚠ Some dependencies may have failed, continuing...${NC}"
fi

echo ""

# Build C++ version
echo "[3] Building C++ executable..."
if make clean > /dev/null 2>&1 && make > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Build successful${NC}"
else
    echo -e "${RED}✗ Build failed${NC}"
    exit 1
fi

echo ""

# Run quick test
echo "[4] Running quick test (2 processors)..."
echo "    This will perform matrix multiplication on 4096x4096 matrices"
echo ""

if mpirun -np 2 ./bin/matrix_operations_mpi 2; then
    echo ""
    echo -e "${GREEN}✓ Test completed successfully${NC}"
else
    echo -e "${RED}✗ Test failed${NC}"
    exit 1
fi

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Run with more processors:"
echo "   make run-custom NP=4 THREADS=4"
echo ""
echo "2. Run scaling analysis:"
echo "   make test-strong-scaling"
echo "   make test-weak-scaling"
echo ""
echo "3. Generate visualizations:"
echo "   make visualize"
echo ""
echo "4. View full documentation:"
echo "   cat README.md"
echo ""
echo "5. Run Python version:"
echo "   make run-python"
echo ""
echo "For help: make help"
echo ""
