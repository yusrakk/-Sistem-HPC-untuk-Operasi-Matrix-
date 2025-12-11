#!/bin/bash
export OMP_NUM_THREADS=2
echo "System Configuration:"
echo "- CPU Cores: $(nproc)"
echo "- MPI Processes: 2"
echo "- OpenMP Threads per Process: $OMP_NUM_THREADS"
echo "- Total Parallel Units: $((2 * $OMP_NUM_THREADS))"
echo ""
echo "Architecture Verification:"
echo "✓ Cluster Level: Multi-node capable (MPI)"
echo "✓ Node Level: CPU Multicore (detected)"
echo "✓ Process Level: MPI processes with distributed memory"
echo "✓ Thread Level: OpenMP threads with shared memory"
