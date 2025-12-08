#!/usr/bin/env python3
"""
Visualization and Reporting Tool for HPC Matrix Operations
Generates graphs and analysis reports for scaling and bottleneck analysis
"""

import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import pandas as pd
import numpy as np
import json
import os
import glob
from datetime import datetime
import seaborn as sns

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 10


class PerformanceVisualizer:
    """Generate visualizations for HPC performance analysis"""
    
    def __init__(self, results_dir="results"):
        self.results_dir = results_dir
        self.output_dir = os.path.join(results_dir, "plots")
        os.makedirs(self.output_dir, exist_ok=True)
        
    def plot_strong_scaling(self, csv_file=None, json_file=None):
        """
        Plot strong scaling results: execution time, speedup, and efficiency
        """
        # Load data
        if csv_file:
            df = pd.read_csv(csv_file)
        elif json_file:
            with open(json_file, 'r') as f:
                data = json.load(f)
            df = pd.DataFrame(data['measurements'])
            df = df[df['success'] == True]
        else:
            # Find latest strong scaling results
            files = glob.glob(os.path.join(self.results_dir, "scaling/strong_scaling_*.csv"))
            if not files:
                print("No strong scaling results found")
                return
            csv_file = max(files, key=os.path.getctime)
            df = pd.read_csv(csv_file)
        
        print(f"Plotting strong scaling from: {csv_file}")
        
        # Create figure with subplots
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('Strong Scaling Analysis - 4096x4096 Matrix', fontsize=16, fontweight='bold')
        
        # 1. Execution Time vs Processors
        ax1 = axes[0, 0]
        ax1.plot(df['num_processors'], df['time'], 'o-', linewidth=2, markersize=8, 
                color='#2E86AB', label='Execution Time')
        ax1.set_xlabel('Number of Processors', fontweight='bold')
        ax1.set_ylabel('Execution Time (seconds)', fontweight='bold')
        ax1.set_title('Execution Time vs Processors')
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        
        # Add values on points
        for i, row in df.iterrows():
            ax1.annotate(f'{row["time"]:.2f}s', 
                        (row['num_processors'], row['time']),
                        textcoords="offset points", xytext=(0,10), ha='center')
        
        # 2. Speedup vs Processors
        ax2 = axes[0, 1]
        ax2.plot(df['num_processors'], df['speedup'], 'o-', linewidth=2, markersize=8,
                color='#A23B72', label='Actual Speedup')
        ax2.plot(df['num_processors'], df['num_processors'], '--', linewidth=2,
                color='#F18F01', label='Ideal (Linear) Speedup')
        ax2.set_xlabel('Number of Processors', fontweight='bold')
        ax2.set_ylabel('Speedup', fontweight='bold')
        ax2.set_title('Speedup vs Processors')
        ax2.grid(True, alpha=0.3)
        ax2.legend()
        
        # Add values on points
        for i, row in df.iterrows():
            ax2.annotate(f'{row["speedup"]:.2f}x', 
                        (row['num_processors'], row['speedup']),
                        textcoords="offset points", xytext=(0,10), ha='center')
        
        # 3. Efficiency vs Processors
        ax3 = axes[1, 0]
        ax3.plot(df['num_processors'], df['efficiency'], 'o-', linewidth=2, markersize=8,
                color='#C73E1D')
        ax3.axhline(y=100, color='#F18F01', linestyle='--', linewidth=2, label='Ideal (100%)')
        ax3.set_xlabel('Number of Processors', fontweight='bold')
        ax3.set_ylabel('Efficiency (%)', fontweight='bold')
        ax3.set_title('Parallel Efficiency vs Processors')
        ax3.set_ylim([0, 110])
        ax3.grid(True, alpha=0.3)
        ax3.legend()
        
        # Add values on points
        for i, row in df.iterrows():
            ax3.annotate(f'{row["efficiency"]:.1f}%', 
                        (row['num_processors'], row['efficiency']),
                        textcoords="offset points", xytext=(0,10), ha='center')
        
        # 4. Summary Table
        ax4 = axes[1, 1]
        ax4.axis('tight')
        ax4.axis('off')
        
        table_data = []
        for _, row in df.iterrows():
            table_data.append([
                int(row['num_processors']),
                f"{row['time']:.3f}s",
                f"{row['speedup']:.2f}x",
                f"{row['efficiency']:.1f}%"
            ])
        
        table = ax4.table(cellText=table_data,
                         colLabels=['Processors', 'Time', 'Speedup', 'Efficiency'],
                         cellLoc='center',
                         loc='center',
                         colWidths=[0.2, 0.25, 0.25, 0.3])
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 2)
        
        # Style header
        for i in range(4):
            table[(0, i)].set_facecolor('#2E86AB')
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        plt.tight_layout()
        
        # Save plot
        output_file = os.path.join(self.output_dir, 'strong_scaling.png')
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"✓ Strong scaling plot saved: {output_file}")
        
        plt.close()
        
        return output_file
    
    def plot_weak_scaling(self, csv_file=None, json_file=None):
        """
        Plot weak scaling results
        """
        # Load data
        if csv_file:
            df = pd.read_csv(csv_file)
        elif json_file:
            with open(json_file, 'r') as f:
                data = json.load(f)
            df = pd.DataFrame(data['measurements'])
            df = df[df['success'] == True]
        else:
            files = glob.glob(os.path.join(self.results_dir, "scaling/weak_scaling_*.csv"))
            if not files:
                print("No weak scaling results found")
                return
            csv_file = max(files, key=os.path.getctime)
            df = pd.read_csv(csv_file)
        
        print(f"Plotting weak scaling from: {csv_file}")
        
        # Create figure
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('Weak Scaling Analysis', fontsize=16, fontweight='bold')
        
        # 1. Execution Time vs Processors
        ax1 = axes[0, 0]
        ax1.plot(df['num_processors'], df['time'], 'o-', linewidth=2, markersize=8,
                color='#2E86AB')
        ax1.set_xlabel('Number of Processors', fontweight='bold')
        ax1.set_ylabel('Execution Time (seconds)', fontweight='bold')
        ax1.set_title('Execution Time vs Processors\n(Constant Work per Processor)')
        ax1.grid(True, alpha=0.3)
        
        for i, row in df.iterrows():
            ax1.annotate(f'{row["time"]:.2f}s', 
                        (row['num_processors'], row['time']),
                        textcoords="offset points", xytext=(0,10), ha='center')
        
        # 2. Efficiency vs Processors
        ax2 = axes[0, 1]
        ax2.plot(df['num_processors'], df['efficiency'], 'o-', linewidth=2, markersize=8,
                color='#A23B72')
        ax2.axhline(y=100, color='#F18F01', linestyle='--', linewidth=2, label='Ideal (100%)')
        ax2.set_xlabel('Number of Processors', fontweight='bold')
        ax2.set_ylabel('Weak Scaling Efficiency (%)', fontweight='bold')
        ax2.set_title('Weak Scaling Efficiency')
        ax2.set_ylim([0, 110])
        ax2.grid(True, alpha=0.3)
        ax2.legend()
        
        for i, row in df.iterrows():
            ax2.annotate(f'{row["efficiency"]:.1f}%', 
                        (row['num_processors'], row['efficiency']),
                        textcoords="offset points", xytext=(0,10), ha='center')
        
        # 3. Matrix Size vs Processors
        ax3 = axes[1, 0]
        ax3.plot(df['num_processors'], df['matrix_size'], 'o-', linewidth=2, markersize=8,
                color='#C73E1D')
        ax3.set_xlabel('Number of Processors', fontweight='bold')
        ax3.set_ylabel('Matrix Size', fontweight='bold')
        ax3.set_title('Problem Size vs Processors')
        ax3.grid(True, alpha=0.3)
        
        # 4. Summary Table
        ax4 = axes[1, 1]
        ax4.axis('tight')
        ax4.axis('off')
        
        table_data = []
        for _, row in df.iterrows():
            table_data.append([
                int(row['num_processors']),
                int(row['matrix_size']),
                f"{row['time']:.3f}s",
                f"{row['efficiency']:.1f}%"
            ])
        
        table = ax4.table(cellText=table_data,
                         colLabels=['Procs', 'Matrix Size', 'Time', 'Efficiency'],
                         cellLoc='center',
                         loc='center',
                         colWidths=[0.2, 0.25, 0.25, 0.25])
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 2)
        
        for i in range(4):
            table[(0, i)].set_facecolor('#2E86AB')
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        plt.tight_layout()
        
        output_file = os.path.join(self.output_dir, 'weak_scaling.png')
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"✓ Weak scaling plot saved: {output_file}")
        
        plt.close()
        
        return output_file
    
    def plot_communication_bottleneck(self, bottleneck_file=None):
        """
        Visualize communication bottleneck analysis
        """
        if not bottleneck_file:
            bottleneck_file = os.path.join(self.results_dir, "bottleneck_analysis.txt")
        
        if not os.path.exists(bottleneck_file):
            print(f"Bottleneck file not found: {bottleneck_file}")
            return
        
        print(f"Analyzing bottleneck from: {bottleneck_file}")
        
        # Parse bottleneck file
        data = []
        with open(bottleneck_file, 'r') as f:
            current_entry = {}
            for line in f:
                line = line.strip()
                if line.startswith("Processors:"):
                    current_entry['processors'] = int(line.split(":")[1].strip())
                elif line.startswith("Avg Computation Time:"):
                    current_entry['comp_time'] = float(line.split(":")[1].strip().split()[0])
                elif line.startswith("Avg Communication Time:"):
                    current_entry['comm_time'] = float(line.split(":")[1].strip().split()[0])
                elif line.startswith("Communication Overhead:"):
                    current_entry['overhead'] = float(line.split(":")[1].strip().replace('%',''))
                elif line.startswith("---") and current_entry:
                    data.append(current_entry)
                    current_entry = {}
        
        if not data:
            print("No bottleneck data found in file")
            return
        
        df = pd.DataFrame(data)
        
        # Create visualization
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        fig.suptitle('Communication Bottleneck Analysis', fontsize=16, fontweight='bold')
        
        # 1. Stacked bar chart: Computation vs Communication time
        ax1 = axes[0]
        x = np.arange(len(df))
        width = 0.6
        
        p1 = ax1.bar(x, df['comp_time'], width, label='Computation', color='#2E86AB')
        p2 = ax1.bar(x, df['comm_time'], width, bottom=df['comp_time'], 
                    label='Communication', color='#C73E1D')
        
        ax1.set_xlabel('Number of Processors', fontweight='bold')
        ax1.set_ylabel('Time (seconds)', fontweight='bold')
        ax1.set_title('Computation vs Communication Time')
        ax1.set_xticks(x)
        ax1.set_xticklabels(df['processors'])
        ax1.legend()
        ax1.grid(True, alpha=0.3, axis='y')
        
        # 2. Communication overhead percentage
        ax2 = axes[1]
        ax2.plot(df['processors'], df['overhead'], 'o-', linewidth=2, markersize=10,
                color='#C73E1D')
        ax2.set_xlabel('Number of Processors', fontweight='bold')
        ax2.set_ylabel('Communication Overhead (%)', fontweight='bold')
        ax2.set_title('Communication Overhead vs Processors')
        ax2.grid(True, alpha=0.3)
        
        for i, row in df.iterrows():
            ax2.annotate(f'{row["overhead"]:.1f}%', 
                        (row['processors'], row['overhead']),
                        textcoords="offset points", xytext=(0,10), ha='center')
        
        plt.tight_layout()
        
        output_file = os.path.join(self.output_dir, 'communication_bottleneck.png')
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"✓ Bottleneck plot saved: {output_file}")
        
        plt.close()
        
        return output_file
    
    def plot_resource_monitoring(self, monitor_dir=None):
        """
        Plot resource monitoring data (CPU, Memory, Network, Disk)
        """
        if not monitor_dir:
            monitor_dir = os.path.join(self.results_dir, "monitoring")
        
        # Find latest monitoring files
        cpu_files = glob.glob(os.path.join(monitor_dir, "monitor_cpu_*.csv"))
        mem_files = glob.glob(os.path.join(monitor_dir, "monitor_memory_*.csv"))
        
        if not cpu_files or not mem_files:
            print("No monitoring data found")
            return
        
        cpu_file = max(cpu_files, key=os.path.getctime)
        mem_file = max(mem_files, key=os.path.getctime)
        
        print(f"Plotting resource monitoring...")
        
        # Load data
        df_cpu = pd.read_csv(cpu_file)
        df_mem = pd.read_csv(mem_file)
        
        # Create visualization
        fig, axes = plt.subplots(2, 1, figsize=(12, 10))
        fig.suptitle('Resource Monitoring During Execution', fontsize=16, fontweight='bold')
        
        # 1. CPU Usage
        ax1 = axes[0]
        ax1.plot(df_cpu['timestamp'], df_cpu['cpu_percent_total'], linewidth=2, color='#2E86AB')
        ax1.fill_between(df_cpu['timestamp'], df_cpu['cpu_percent_total'], alpha=0.3, color='#2E86AB')
        ax1.set_xlabel('Time (seconds)', fontweight='bold')
        ax1.set_ylabel('CPU Usage (%)', fontweight='bold')
        ax1.set_title('CPU Utilization Over Time')
        ax1.set_ylim([0, 100])
        ax1.grid(True, alpha=0.3)
        
        # 2. Memory Usage
        ax2 = axes[1]
        ax2.plot(df_mem['timestamp'], df_mem['percent'], linewidth=2, color='#A23B72')
        ax2.fill_between(df_mem['timestamp'], df_mem['percent'], alpha=0.3, color='#A23B72')
        ax2.set_xlabel('Time (seconds)', fontweight='bold')
        ax2.set_ylabel('Memory Usage (%)', fontweight='bold')
        ax2.set_title('Memory Utilization Over Time')
        ax2.set_ylim([0, 100])
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        output_file = os.path.join(self.output_dir, 'resource_monitoring.png')
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"✓ Resource monitoring plot saved: {output_file}")
        
        plt.close()
        
        return output_file
    
    def generate_report(self):
        """
        Generate comprehensive HTML report
        """
        print("\n" + "="*70)
        print("Generating Performance Analysis Report")
        print("="*70)
        
        # Generate all plots
        plots = {}
        
        try:
            plots['strong_scaling'] = self.plot_strong_scaling()
        except Exception as e:
            print(f"Warning: Could not generate strong scaling plot: {e}")
        
        try:
            plots['weak_scaling'] = self.plot_weak_scaling()
        except Exception as e:
            print(f"Warning: Could not generate weak scaling plot: {e}")
        
        try:
            plots['bottleneck'] = self.plot_communication_bottleneck()
        except Exception as e:
            print(f"Warning: Could not generate bottleneck plot: {e}")
        
        try:
            plots['monitoring'] = self.plot_resource_monitoring()
        except Exception as e:
            print(f"Warning: Could not generate monitoring plot: {e}")
        
        print("\n" + "="*70)
        print("Report Generation Complete")
        print("="*70)
        print(f"Plots saved to: {self.output_dir}")
        print("\nGenerated plots:")
        for name, path in plots.items():
            if path:
                print(f"  - {name}: {path}")


def main():
    import sys
    
    visualizer = PerformanceVisualizer()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "strong":
            visualizer.plot_strong_scaling()
        elif command == "weak":
            visualizer.plot_weak_scaling()
        elif command == "bottleneck":
            visualizer.plot_communication_bottleneck()
        elif command == "monitoring":
            visualizer.plot_resource_monitoring()
        elif command == "all" or command == "report":
            visualizer.generate_report()
        else:
            print(f"Unknown command: {command}")
            print("Usage: python3 visualize.py [strong|weak|bottleneck|monitoring|all]")
    else:
        # Generate all plots
        visualizer.generate_report()


if __name__ == "__main__":
    main()
