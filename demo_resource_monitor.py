#!/usr/bin/env python3
"""
Demo: Resource Monitoring System
Demonstrates how to use ResourceMonitor for tracking system resources
"""

from src.resource_monitor import ResourceMonitor
import time
import numpy as np

def simulate_heavy_computation():
    """Simulate heavy computation to generate resource usage"""
    print("\n🔄 Running heavy computation (simulating matrix operations)...")
    
    # Create large matrices
    size = 2048
    print(f"   Creating matrices ({size}×{size})...")
    A = np.random.rand(size, size)
    B = np.random.rand(size, size)
    
    # Perform multiplication (CPU intensive)
    print(f"   Performing matrix multiplication...")
    C = np.dot(A, B)
    
    # Some additional operations
    print(f"   Additional operations...")
    D = np.linalg.inv(A[:1024, :1024])  # Smaller inversion
    E = np.transpose(C)
    F = C + E
    
    print(f"   ✅ Computation done!")
    return C

def main():
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║        📊 RESOURCE MONITORING DEMO                           ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    
    # Create monitor instance
    monitor = ResourceMonitor(log_dir="results/monitoring", interval=0.5)
    
    print("\n1️⃣ Starting resource monitoring...")
    monitor.start()
    
    print("\n2️⃣ Waiting 2 seconds (baseline measurement)...")
    time.sleep(2)
    
    print("\n3️⃣ Running computation...")
    result = simulate_heavy_computation()
    
    print("\n4️⃣ Waiting 2 seconds (cooldown)...")
    time.sleep(2)
    
    print("\n5️⃣ Stopping monitor...")
    monitor.stop()
    
    print("\n6️⃣ Saving logs...")
    monitor.save_logs(prefix="demo")
    
    print("\n7️⃣ Getting summary...")
    summary = monitor.get_summary()
    
    print("\n" + "━"*68)
    print("📊 MONITORING RESULTS SUMMARY")
    print("━"*68)
    print(f"Duration:          {summary['duration']:.2f} seconds")
    print(f"")
    print(f"CPU Usage:")
    print(f"  Average:         {summary['cpu_avg']:.1f}%")
    print(f"  Maximum:         {summary['cpu_max']:.1f}%")
    print(f"")
    print(f"Memory Usage:")
    print(f"  Average:         {summary['memory_avg_mb']:.1f} MB")
    print(f"  Maximum:         {summary['memory_max_mb']:.1f} MB")
    print(f"  Peak Percent:    {summary['memory_max_percent']:.1f}%")
    print(f"")
    print(f"Network I/O:")
    print(f"  Total Sent:      {summary['network_total_sent_mb']:.2f} MB")
    print(f"  Total Received:  {summary['network_total_recv_mb']:.2f} MB")
    print(f"")
    print(f"Disk I/O:")
    print(f"  Total Read:      {summary['disk_total_read_mb']:.2f} MB")
    print(f"  Total Write:     {summary['disk_total_write_mb']:.2f} MB")
    print("━"*68)
    
    print("\n✅ Demo complete!")
    print("\n📂 Log files saved in: results/monitoring/")
    print("   - demo_cpu_*.csv")
    print("   - demo_memory_*.csv")
    print("   - demo_network_*.csv")
    print("   - demo_disk_*.csv")
    print("   - demo_summary_*.json")
    
    print("\n💡 Visualize dengan:")
    print("   python3 scripts/visualize.py monitoring")

if __name__ == "__main__":
    main()
