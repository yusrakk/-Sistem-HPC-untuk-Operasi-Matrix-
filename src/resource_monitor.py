#!/usr/bin/env python3
"""
Resource Monitoring System for HPC Matrix Operations
Monitors CPU, Memory, Network, and Disk I/O during computation
"""

import psutil
import time
import json
import os
from datetime import datetime
from threading import Thread
import csv

class ResourceMonitor:
    """Comprehensive resource monitoring for HPC operations"""
    
    def __init__(self, log_dir="results/monitoring", interval=0.5):
        self.log_dir = log_dir
        self.interval = interval
        self.monitoring = False
        self.monitor_thread = None
        
        # Create log directory
        os.makedirs(log_dir, exist_ok=True)
        
        # Initialize data storage
        self.cpu_data = []
        self.memory_data = []
        self.network_data = []
        self.disk_data = []
        
        # Get initial network and disk I/O counters
        self.net_io_start = psutil.net_io_counters()
        self.disk_io_start = psutil.disk_io_counters()
        
    def start(self):
        """Start monitoring in background thread"""
        self.monitoring = True
        self.monitor_thread = Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        print(f"[Monitor] Started resource monitoring (interval: {self.interval}s)")
        
    def stop(self):
        """Stop monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
        print("[Monitor] Stopped resource monitoring")
        
    def _monitor_loop(self):
        """Main monitoring loop"""
        start_time = time.time()
        
        while self.monitoring:
            timestamp = time.time() - start_time
            
            # CPU monitoring
            cpu_percent = psutil.cpu_percent(interval=None, percpu=True)
            cpu_freq = psutil.cpu_freq()
            
            self.cpu_data.append({
                'timestamp': timestamp,
                'cpu_percent_total': psutil.cpu_percent(interval=None),
                'cpu_percent_per_core': cpu_percent,
                'cpu_freq_current': cpu_freq.current if cpu_freq else 0,
                'num_cores': psutil.cpu_count(),
                'load_avg': os.getloadavg() if hasattr(os, 'getloadavg') else [0, 0, 0]
            })
            
            # Memory monitoring
            mem = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            self.memory_data.append({
                'timestamp': timestamp,
                'total_mb': mem.total / (1024**2),
                'available_mb': mem.available / (1024**2),
                'used_mb': mem.used / (1024**2),
                'percent': mem.percent,
                'swap_total_mb': swap.total / (1024**2),
                'swap_used_mb': swap.used / (1024**2),
                'swap_percent': swap.percent
            })
            
            # Network monitoring
            net_io = psutil.net_io_counters()
            
            self.network_data.append({
                'timestamp': timestamp,
                'bytes_sent': net_io.bytes_sent - self.net_io_start.bytes_sent,
                'bytes_recv': net_io.bytes_recv - self.net_io_start.bytes_recv,
                'packets_sent': net_io.packets_sent - self.net_io_start.packets_sent,
                'packets_recv': net_io.packets_recv - self.net_io_start.packets_recv,
                'errin': net_io.errin,
                'errout': net_io.errout
            })
            
            # Disk I/O monitoring
            disk_io = psutil.disk_io_counters()
            
            self.disk_data.append({
                'timestamp': timestamp,
                'read_bytes': disk_io.read_bytes - self.disk_io_start.read_bytes,
                'write_bytes': disk_io.write_bytes - self.disk_io_start.write_bytes,
                'read_count': disk_io.read_count - self.disk_io_start.read_count,
                'write_count': disk_io.write_count - self.disk_io_start.write_count
            })
            
            time.sleep(self.interval)
    
    def save_logs(self, prefix="monitor"):
        """Save monitoring data to files"""
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save CPU data
        cpu_file = os.path.join(self.log_dir, f"{prefix}_cpu_{timestamp_str}.csv")
        with open(cpu_file, 'w', newline='') as f:
            if self.cpu_data:
                writer = csv.DictWriter(f, fieldnames=['timestamp', 'cpu_percent_total', 
                                                       'cpu_freq_current', 'num_cores'])
                writer.writeheader()
                for row in self.cpu_data:
                    writer.writerow({
                        'timestamp': row['timestamp'],
                        'cpu_percent_total': row['cpu_percent_total'],
                        'cpu_freq_current': row['cpu_freq_current'],
                        'num_cores': row['num_cores']
                    })
        
        # Save memory data
        mem_file = os.path.join(self.log_dir, f"{prefix}_memory_{timestamp_str}.csv")
        with open(mem_file, 'w', newline='') as f:
            if self.memory_data:
                writer = csv.DictWriter(f, fieldnames=self.memory_data[0].keys())
                writer.writeheader()
                writer.writerows(self.memory_data)
        
        # Save network data
        net_file = os.path.join(self.log_dir, f"{prefix}_network_{timestamp_str}.csv")
        with open(net_file, 'w', newline='') as f:
            if self.network_data:
                writer = csv.DictWriter(f, fieldnames=self.network_data[0].keys())
                writer.writeheader()
                writer.writerows(self.network_data)
        
        # Save disk data
        disk_file = os.path.join(self.log_dir, f"{prefix}_disk_{timestamp_str}.csv")
        with open(disk_file, 'w', newline='') as f:
            if self.disk_data:
                writer = csv.DictWriter(f, fieldnames=self.disk_data[0].keys())
                writer.writeheader()
                writer.writerows(self.disk_data)
        
        # Save summary
        summary = self.get_summary()
        summary_file = os.path.join(self.log_dir, f"{prefix}_summary_{timestamp_str}.json")
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"[Monitor] Logs saved to {self.log_dir}")
        return {
            'cpu': cpu_file,
            'memory': mem_file,
            'network': net_file,
            'disk': disk_file,
            'summary': summary_file
        }
    
    def get_summary(self):
        """Generate summary statistics"""
        summary = {
            'timestamp': datetime.now().isoformat(),
            'duration_seconds': self.cpu_data[-1]['timestamp'] if self.cpu_data else 0,
            'samples_collected': len(self.cpu_data)
        }
        
        # CPU summary
        if self.cpu_data:
            cpu_percents = [d['cpu_percent_total'] for d in self.cpu_data]
            summary['cpu'] = {
                'avg_percent': sum(cpu_percents) / len(cpu_percents),
                'max_percent': max(cpu_percents),
                'min_percent': min(cpu_percents),
                'num_cores': self.cpu_data[0]['num_cores']
            }
        
        # Memory summary
        if self.memory_data:
            mem_percents = [d['percent'] for d in self.memory_data]
            mem_used = [d['used_mb'] for d in self.memory_data]
            summary['memory'] = {
                'avg_percent': sum(mem_percents) / len(mem_percents),
                'max_percent': max(mem_percents),
                'peak_used_mb': max(mem_used),
                'total_mb': self.memory_data[0]['total_mb']
            }
        
        # Network summary
        if self.network_data:
            summary['network'] = {
                'total_sent_mb': self.network_data[-1]['bytes_sent'] / (1024**2),
                'total_recv_mb': self.network_data[-1]['bytes_recv'] / (1024**2),
                'total_packets_sent': self.network_data[-1]['packets_sent'],
                'total_packets_recv': self.network_data[-1]['packets_recv']
            }
        
        # Disk summary
        if self.disk_data:
            summary['disk'] = {
                'total_read_mb': self.disk_data[-1]['read_bytes'] / (1024**2),
                'total_write_mb': self.disk_data[-1]['write_bytes'] / (1024**2),
                'total_read_ops': self.disk_data[-1]['read_count'],
                'total_write_ops': self.disk_data[-1]['write_count']
            }
        
        return summary
    
    def print_summary(self):
        """Print summary to console"""
        summary = self.get_summary()
        
        print("\n" + "="*60)
        print("Resource Monitoring Summary")
        print("="*60)
        print(f"Duration: {summary['duration_seconds']:.2f} seconds")
        print(f"Samples: {summary['samples_collected']}")
        
        if 'cpu' in summary:
            print(f"\nCPU:")
            print(f"  Cores: {summary['cpu']['num_cores']}")
            print(f"  Avg Usage: {summary['cpu']['avg_percent']:.2f}%")
            print(f"  Peak Usage: {summary['cpu']['max_percent']:.2f}%")
        
        if 'memory' in summary:
            print(f"\nMemory:")
            print(f"  Total: {summary['memory']['total_mb']:.2f} MB")
            print(f"  Peak Used: {summary['memory']['peak_used_mb']:.2f} MB")
            print(f"  Avg Usage: {summary['memory']['avg_percent']:.2f}%")
            print(f"  Peak Usage: {summary['memory']['max_percent']:.2f}%")
        
        if 'network' in summary:
            print(f"\nNetwork:")
            print(f"  Sent: {summary['network']['total_sent_mb']:.2f} MB")
            print(f"  Received: {summary['network']['total_recv_mb']:.2f} MB")
            print(f"  Packets Sent: {summary['network']['total_packets_sent']}")
            print(f"  Packets Received: {summary['network']['total_packets_recv']}")
        
        if 'disk' in summary:
            print(f"\nDisk I/O:")
            print(f"  Read: {summary['disk']['total_read_mb']:.2f} MB")
            print(f"  Write: {summary['disk']['total_write_mb']:.2f} MB")
            print(f"  Read Ops: {summary['disk']['total_read_ops']}")
            print(f"  Write Ops: {summary['disk']['total_write_ops']}")
        
        print("="*60)


def main():
    """Test resource monitoring"""
    print("Testing Resource Monitor...")
    
    monitor = ResourceMonitor(interval=0.1)
    monitor.start()
    
    # Simulate some work
    print("Simulating workload for 5 seconds...")
    import numpy as np
    
    for i in range(5):
        # Some computation
        A = np.random.rand(1000, 1000)
        B = np.random.rand(1000, 1000)
        C = np.dot(A, B)
        time.sleep(1)
        print(f"  Iteration {i+1}/5")
    
    monitor.stop()
    monitor.print_summary()
    
    # Save logs
    files = monitor.save_logs(prefix="test")
    print(f"\nLog files saved:")
    for key, path in files.items():
        print(f"  {key}: {path}")


if __name__ == "__main__":
    main()
