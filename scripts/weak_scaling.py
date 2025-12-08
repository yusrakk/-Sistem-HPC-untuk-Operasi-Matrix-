#!/usr/bin/env python3
"""
Weak Scaling Analysis Script
Tests how execution time changes when both problem size and number of processors
increase proportionally (constant work per processor)
"""

import subprocess
import time
import json
import os
import sys
from datetime import datetime
import csv

def run_weak_scaling_test(executable_template, scaling_configs, 
                          num_threads=4, test_name="weak_scaling"):
    """
    Run weak scaling analysis
    
    Args:
        executable_template: Path template to executable
        scaling_configs: List of (num_processors, matrix_size) tuples
        num_threads: Number of OpenMP threads per process
        test_name: Name for the test run
    """
    
    results_dir = "results/scaling"
    os.makedirs(results_dir, exist_ok=True)
    
    results = {
        "test_name": test_name,
        "test_type": "weak_scaling",
        "num_threads": num_threads,
        "timestamp": datetime.now().isoformat(),
        "measurements": []
    }
    
    print("="*70)
    print(f"Weak Scaling Analysis: {test_name}")
    print("="*70)
    print(f"OpenMP Threads per Process: {num_threads}")
    print(f"Scaling: Constant work per processor")
    print("="*70)
    
    base_time = None
    
    for num_procs, matrix_size in scaling_configs:
        print(f"\n[Test] {num_procs} processor(s), {matrix_size}x{matrix_size} matrix")
        print(f"       Work per processor: {(matrix_size**2)/(num_procs):.0f} elements")
        
        # For Python script with dynamic matrix size, we need to modify approach
        # This is a simplified version - actual implementation may need wrapper
        executable = executable_template
        is_python = executable.endswith('.py')
        
        # Build command
        if is_python:
            cmd = [
                "mpirun",
                "-np", str(num_procs),
                "python3", executable
            ]
        else:
            cmd = [
                "mpirun",
                "-np", str(num_procs),
                executable,
                str(num_threads)
            ]
        
        # Run test
        start_time = time.time()
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout
            )
            
            elapsed_time = time.time() - start_time
            
            # Parse output for actual computation time
            output_lines = result.stdout.split('\n')
            computation_time = elapsed_time
            
            for line in output_lines:
                if "Completed in" in line or "seconds" in line:
                    try:
                        words = line.split()
                        for i, word in enumerate(words):
                            if word == "in" and i+1 < len(words):
                                computation_time = float(words[i+1])
                                break
                    except:
                        pass
            
            print(f"   ✓ Completed in {computation_time:.4f} seconds")
            
            # Set base time from first measurement
            if base_time is None:
                base_time = computation_time
            
            # Calculate efficiency (ideally stays constant in weak scaling)
            efficiency = (base_time / computation_time) * 100 if computation_time > 0 else 0
            
            measurement = {
                "num_processors": num_procs,
                "matrix_size": matrix_size,
                "work_per_processor": (matrix_size**2) / num_procs,
                "time": computation_time,
                "efficiency": efficiency,
                "wall_time": elapsed_time,
                "success": True
            }
            
            print(f"   Weak Scaling Efficiency: {efficiency:.2f}%")
            
        except subprocess.TimeoutExpired:
            print(f"   ✗ Timeout after 10 minutes")
            measurement = {
                "num_processors": num_procs,
                "matrix_size": matrix_size,
                "work_per_processor": (matrix_size**2) / num_procs,
                "time": None,
                "efficiency": None,
                "success": False,
                "error": "timeout"
            }
        except Exception as e:
            print(f"   ✗ Error: {str(e)}")
            measurement = {
                "num_processors": num_procs,
                "matrix_size": matrix_size,
                "work_per_processor": (matrix_size**2) / num_procs,
                "time": None,
                "efficiency": None,
                "success": False,
                "error": str(e)
            }
        
        results["measurements"].append(measurement)
        time.sleep(2)
    
    # Save results
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_file = os.path.join(results_dir, f"weak_scaling_{timestamp_str}.json")
    csv_file = os.path.join(results_dir, f"weak_scaling_{timestamp_str}.csv")
    
    with open(json_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    # Save CSV
    with open(csv_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['num_processors', 'matrix_size', 
                                               'work_per_processor', 'time', 'efficiency'])
        writer.writeheader()
        for m in results["measurements"]:
            if m["success"]:
                writer.writerow({
                    'num_processors': m['num_processors'],
                    'matrix_size': m['matrix_size'],
                    'work_per_processor': m['work_per_processor'],
                    'time': m['time'],
                    'efficiency': m['efficiency']
                })
    
    print("\n" + "="*70)
    print("Weak Scaling Analysis Complete")
    print("="*70)
    print(f"Results saved to:")
    print(f"  JSON: {json_file}")
    print(f"  CSV:  {csv_file}")
    
    return results


def print_summary(results):
    """Print summary of scaling results"""
    print("\n" + "="*70)
    print("Summary")
    print("="*70)
    print(f"{'Procs':<8} {'Matrix Size':<12} {'Work/Proc':<15} {'Time (s)':<12} {'Efficiency':<12}")
    print("-"*70)
    
    for m in results["measurements"]:
        if m["success"]:
            print(f"{m['num_processors']:<8} {m['matrix_size']:<12} "
                  f"{m['work_per_processor']:<15.0f} {m['time']:<12.4f} {m['efficiency']:<12.2f}%")
    
    print("="*70)


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 weak_scaling.py <executable>")
        print("Example: python3 weak_scaling.py ./bin/matrix_operations_mpi")
        print("Example: python3 weak_scaling.py src/matrix_operations_python.py")
        sys.exit(1)
    
    executable = sys.argv[1]
    
    if not os.path.exists(executable):
        print(f"Error: Executable not found: {executable}")
        sys.exit(1)
    
    # Weak scaling: increase both processors and problem size proportionally
    # Keep work per processor approximately constant
    # Format: (num_processors, matrix_size)
    scaling_configs = [
        (1, 2048),   # Base case: 1 proc, 2048x2048
        (2, 2896),   # 2 procs: 2896x2896 (≈2x work)
        (4, 4096),   # 4 procs: 4096x4096 (≈4x work)
        (8, 5792),   # 8 procs: 5792x5792 (≈8x work)
    ]
    
    print("\nNote: This script runs the default 4096x4096 matrix.")
    print("For true weak scaling, you would need to modify the source code")
    print("to accept matrix size as a parameter.\n")
    
    # For now, test with constant matrix size (this is actually strong scaling)
    # but we keep the framework for when dynamic sizing is implemented
    scaling_configs_simplified = [
        (1, 4096),
        (2, 4096),
        (4, 4096),
        (8, 4096),
    ]
    
    results = run_weak_scaling_test(
        executable_template=executable,
        scaling_configs=scaling_configs_simplified,
        num_threads=4,
        test_name="weak_scaling_test"
    )
    
    print_summary(results)


if __name__ == "__main__":
    main()
