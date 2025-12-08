#!/usr/bin/env python3
"""
Complete Demo Script - Runs full HPC system demonstration
Includes: Matrix operations, scaling tests, and visualization
"""

import subprocess
import os
import sys
import time
from datetime import datetime

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(70)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}\n")

def print_step(step_num, text):
    print(f"{Colors.OKBLUE}[Step {step_num}]{Colors.ENDC} {text}")

def print_success(text):
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")

def print_error(text):
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")

def run_command(cmd, description, timeout=600):
    """Run a shell command and handle output"""
    print(f"\n{Colors.OKCYAN}Running: {description}{Colors.ENDC}")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        start = time.time()
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        elapsed = time.time() - start
        
        if result.returncode == 0:
            print_success(f"Completed in {elapsed:.2f} seconds")
            return True
        else:
            print_error(f"Failed with return code {result.returncode}")
            if result.stderr:
                print(f"Error: {result.stderr[:500]}")
            return False
    except subprocess.TimeoutExpired:
        print_error(f"Timeout after {timeout} seconds")
        return False
    except Exception as e:
        print_error(f"Exception: {str(e)}")
        return False

def main():
    print_header("HPC Matrix Operations - Complete Demo")
    
    # Check if in correct directory
    if not os.path.exists("Makefile"):
        print_error("Please run this script from the project root directory")
        sys.exit(1)
    
    print(f"Demo started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"This demo will take approximately 10-15 minutes")
    
    # Step 1: Build
    print_step(1, "Building C++ executable")
    if not run_command(["make", "clean"], "Clean build"):
        print_error("Failed to clean build")
        sys.exit(1)
    
    if not run_command(["make"], "Build executable"):
        print_error("Build failed - check OpenMPI installation")
        sys.exit(1)
    
    # Step 2: Quick matrix operation test
    print_step(2, "Running matrix operations (quick test with 2 processors)")
    if not run_command(
        ["mpirun", "-np", "2", "./bin/matrix_operations_mpi", "2"],
        "Matrix operations test",
        timeout=300
    ):
        print_error("Matrix operations test failed")
        sys.exit(1)
    
    # Step 3: Strong scaling analysis
    print_step(3, "Running strong scaling analysis")
    print("Testing with 1, 2, 4 processors...")
    
    if not run_command(
        ["python3", "scripts/strong_scaling.py", "./bin/matrix_operations_mpi"],
        "Strong scaling test",
        timeout=600
    ):
        print_error("Strong scaling test failed")
    else:
        print_success("Strong scaling data collected")
    
    # Step 4: Test Python version (quick)
    print_step(4, "Testing Python implementation")
    if not run_command(
        ["mpirun", "-np", "2", "python3", "src/matrix_operations_python.py"],
        "Python version test",
        timeout=300
    ):
        print_error("Python version test failed")
    else:
        print_success("Python implementation verified")
    
    # Step 5: Test distributed storage
    print_step(5, "Testing distributed storage system")
    if not run_command(
        ["python3", "src/distributed_storage.py"],
        "Distributed storage test"
    ):
        print_error("Distributed storage test failed")
    else:
        print_success("Distributed storage working")
    
    # Step 6: Generate visualizations
    print_step(6, "Generating visualizations and reports")
    if not run_command(
        ["python3", "scripts/visualize.py", "all"],
        "Generate all plots"
    ):
        print_error("Visualization generation failed")
    else:
        print_success("Visualizations generated")
    
    # Summary
    print_header("Demo Complete!")
    
    print("\n📊 Results and Output Files:\n")
    
    # Check for generated files
    files_to_check = [
        ("results/performance_log.csv", "Performance logs"),
        ("results/bottleneck_analysis.txt", "Bottleneck analysis"),
        ("results/plots/strong_scaling.png", "Strong scaling plot"),
        ("results/plots/communication_bottleneck.png", "Bottleneck plot"),
    ]
    
    for filepath, description in files_to_check:
        if os.path.exists(filepath):
            size = os.path.getsize(filepath)
            print(f"  {Colors.OKGREEN}✓{Colors.ENDC} {description}: {filepath} ({size} bytes)")
        else:
            print(f"  {Colors.WARNING}⚠{Colors.ENDC} {description}: Not generated")
    
    print("\n📈 Key Metrics:\n")
    
    # Try to read some metrics
    if os.path.exists("results/performance_log.csv"):
        try:
            with open("results/performance_log.csv", 'r') as f:
                lines = f.readlines()
                if len(lines) > 1:
                    print(f"  • Total operations logged: {len(lines) - 1}")
        except:
            pass
    
    print("\n🎯 Next Steps:\n")
    print("  1. View plots in: results/plots/")
    print("  2. Check performance logs: results/performance_log.csv")
    print("  3. Review bottleneck analysis: results/bottleneck_analysis.txt")
    print("  4. Run with more processors: make run-custom NP=8 THREADS=4")
    print("  5. Run full scaling tests: make test-all-scaling")
    
    print(f"\n{Colors.OKGREEN}Demo completed successfully!{Colors.ENDC}\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.WARNING}Demo interrupted by user{Colors.ENDC}")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n{Colors.FAIL}Demo failed with error: {str(e)}{Colors.ENDC}")
        sys.exit(1)
