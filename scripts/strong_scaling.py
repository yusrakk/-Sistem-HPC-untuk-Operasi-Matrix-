#!/usr/bin/env python3
"""
Strong Scaling Analysis Script
Tests how execution time changes with increasing number of processors
while keeping problem size constant (4096x4096)
"""

import subprocess
import time
import json
import os
import sys
from datetime import datetime
import csv

def run_scaling_test(executable, num_processors_list, matrix_size=4096, 
                     num_threads=4, test_name="strong_scaling"):
    """
    Run strong scaling analysis
    
    Args:
        executable: Path to the executable (C++ or Python script)
        num_processors_list: List of processor counts to test
        matrix_size: Size of the matrix (constant for strong scaling)
        num_threads: Number of OpenMP threads per process
        test_name: Name for the test run
    """
    
    results_dir = "results/scaling"
    os.makedirs(results_dir, exist_ok=True)
    
    results = {
        "test_name": test_name,
        "test_type": "strong_scaling",
        "matrix_size": matrix_size,
        "num_threads": num_threads,
        "timestamp": datetime.now().isoformat(),
        "measurements": []
    }
    
    print("="*70)
    print(f"Strong Scaling Analysis: {test_name}")
    print("="*70)
    print(f"Matrix Size: {matrix_size}x{matrix_size} (constant)")
    print(f"OpenMP Threads per Process: {num_threads}")
    print(f"Testing with processors: {num_processors_list}")
    print("="*70)
    
    # Determine if C++ or Python
    is_python = executable.endswith('.py')
    
    for num_procs in num_processors_list:
        print(f"\n[Test] Running with {num_procs} processor(s)...")
        
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
            computation_time = elapsed_time  # Default to wall time
            
            for line in output_lines:
                if "Completed in" in line or "seconds" in line:
                    # Try to extract time from output
                    try:
                        words = line.split()
                        for i, word in enumerate(words):
                            if word == "in" and i+1 < len(words):
                                computation_time = float(words[i+1])
                                break
                    except:
                        pass
            
            print(f"   ✓ Completed in {computation_time:.4f} seconds")
            
            # Calculate metrics
            speedup = results["measurements"][0]["time"] / computation_time if results["measurements"] else 1.0
            efficiency = (speedup / num_procs) * 100 if num_procs > 0 else 0
            
            measurement = {
                "num_processors": num_procs,
                "time": computation_time,
                "speedup": speedup,
                "efficiency": efficiency,
                "wall_time": elapsed_time,
                "success": True
            }
            
            print(f"   Speedup: {speedup:.2f}x")
            print(f"   Efficiency: {efficiency:.2f}%")
            
        except subprocess.TimeoutExpired:
            print(f"   ✗ Timeout after 10 minutes")
            measurement = {
                "num_processors": num_procs,
                "time": None,
                "speedup": None,
                "efficiency": None,
                "success": False,
                "error": "timeout"
            }
        except Exception as e:
            print(f"   ✗ Error: {str(e)}")
            measurement = {
                "num_processors": num_procs,
                "time": None,
                "speedup": None,
                "efficiency": None,
                "success": False,
                "error": str(e)
            }
        
        results["measurements"].append(measurement)
        time.sleep(2)  # Brief pause between tests
    
    # Save results
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_file = os.path.join(results_dir, f"strong_scaling_{timestamp_str}.json")
    csv_file = os.path.join(results_dir, f"strong_scaling_{timestamp_str}.csv")
    
    with open(json_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    # Save CSV for easy plotting
    with open(csv_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['num_processors', 'time', 'speedup', 'efficiency'])
        writer.writeheader()
        for m in results["measurements"]:
            if m["success"]:
                writer.writerow({
                    'num_processors': m['num_processors'],
                    'time': m['time'],
                    'speedup': m['speedup'],
                    'efficiency': m['efficiency']
                })
    
    print("\n" + "="*70)
    print("Strong Scaling Analysis Complete")
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
    print(f"{'Processors':<12} {'Time (s)':<12} {'Speedup':<12} {'Efficiency':<12}")
    print("-"*70)
    
    for m in results["measurements"]:
        if m["success"]:
            print(f"{m['num_processors']:<12} {m['time']:<12.4f} {m['speedup']:<12.2f} {m['efficiency']:<12.2f}%")
    
    print("="*70)


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 strong_scaling.py <executable>")
        print("Example: python3 strong_scaling.py ./bin/matrix_operations_mpi")
        print("Example: python3 strong_scaling.py src/matrix_operations_python.py")
        sys.exit(1)
    
    executable = sys.argv[1]
    
    if not os.path.exists(executable):
        print(f"Error: Executable not found: {executable}")
        sys.exit(1)
    
    # Test with 1, 2, 4, 8 processors
    # Adjust based on your system's available cores
    num_processors_list = [1, 2, 4, 8]
    
    results = run_scaling_test(
        executable=executable,
        num_processors_list=num_processors_list,
        matrix_size=4096,
        num_threads=4,
        test_name="strong_scaling_4096"
    )
    
    print_summary(results)


if __name__ == "__main__":
    main()
