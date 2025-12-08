# Compiler and flags
CXX = mpic++
CXXFLAGS = -O3 -Wall -std=c++11 -fopenmp
LDFLAGS = -fopenmp

# Directories
SRC_DIR = src
BIN_DIR = bin
OBJ_DIR = obj

# Targets
TARGET = $(BIN_DIR)/matrix_operations_mpi
SOURCES = $(SRC_DIR)/matrix_operations_mpi.cpp
OBJECTS = $(OBJ_DIR)/matrix_operations_mpi.o

# Default target
all: directories $(TARGET)

# Create necessary directories
directories:
	@mkdir -p $(BIN_DIR)
	@mkdir -p $(OBJ_DIR)
	@mkdir -p data
	@mkdir -p results
	@mkdir -p results/monitoring
	@mkdir -p results/scaling
	@mkdir -p results/plots

# Compile object files
$(OBJ_DIR)/%.o: $(SRC_DIR)/%.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@

# Link executable
$(TARGET): $(OBJECTS)
	$(CXX) $(CXXFLAGS) $(OBJECTS) -o $(TARGET) $(LDFLAGS)
	@echo "Build complete: $(TARGET)"

# Run with default settings (4 processes, 4 threads)
run: $(TARGET)
	mpirun -np 4 $(TARGET) 4

# Run with custom settings
# Usage: make run-custom NP=8 THREADS=4
run-custom: $(TARGET)
	mpirun -np $(NP) $(TARGET) $(THREADS)

# Python version using mpi4py
run-python:
	mpirun -np 4 python3 $(SRC_DIR)/matrix_operations_python.py

# Strong scaling analysis
test-strong-scaling: $(TARGET)
	@echo "Running strong scaling analysis..."
	python3 scripts/strong_scaling.py $(TARGET)

# Weak scaling analysis
test-weak-scaling: $(TARGET)
	@echo "Running weak scaling analysis..."
	python3 scripts/weak_scaling.py $(TARGET)

# Run all scaling tests
test-all-scaling: test-strong-scaling test-weak-scaling
	@echo "All scaling tests complete"

# Generate visualization
visualize:
	python3 scripts/visualize.py all

# Test distributed storage
test-storage:
	python3 src/distributed_storage.py

# Test resource monitor
test-monitor:
	python3 src/resource_monitor.py

# Clean build artifacts
clean:
	rm -rf $(BIN_DIR) $(OBJ_DIR)
	@echo "Cleaned build artifacts"

# Clean all generated data and results
clean-all: clean
	rm -rf data/*.dat data/*.npy data/*.h5 data/distributed
	rm -rf results/*.csv results/*.txt results/*.json
	rm -rf results/monitoring/* results/scaling/* results/plots/*
	@echo "Cleaned all data and results"

# Install Python dependencies
install-deps:
	pip3 install -r requirements.txt
	@echo "Python dependencies installed"

# Check MPI installation
check-mpi:
	@echo "Checking MPI installation..."
	@which mpirun || echo "Error: mpirun not found"
	@which mpic++ || echo "Error: mpic++ not found"
	@mpirun --version || echo "Error: Cannot run mpirun"

# Display help
help:
	@echo "Available targets:"
	@echo "  all                  - Build C++ executable (default)"
	@echo "  run                  - Run with 4 processes and 4 threads"
	@echo "  run-custom           - Run with custom settings (NP=<procs> THREADS=<threads>)"
	@echo "  run-python           - Run Python version with mpi4py"
	@echo "  test-strong-scaling  - Run strong scaling analysis"
	@echo "  test-weak-scaling    - Run weak scaling analysis"
	@echo "  test-all-scaling     - Run all scaling tests"
	@echo "  visualize            - Generate all plots and visualizations"
	@echo "  test-storage         - Test distributed storage system"
	@echo "  test-monitor         - Test resource monitoring system"
	@echo "  clean                - Clean build artifacts"
	@echo "  clean-all            - Clean all data and results"
	@echo "  install-deps         - Install Python dependencies"
	@echo "  check-mpi            - Check MPI installation"
	@echo "  help                 - Display this help message"
	@echo ""
	@echo "Examples:"
	@echo "  make run"
	@echo "  make run-custom NP=8 THREADS=4"
	@echo "  make test-strong-scaling"
	@echo "  make visualize"

.PHONY: all directories run run-custom run-python test-strong-scaling test-weak-scaling \
        test-all-scaling visualize test-storage test-monitor clean clean-all \
        install-deps check-mpi help
