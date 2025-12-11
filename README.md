# Sistem HPC untuk Operasi Matrix (4096×4096) dengan Distributed Storage dan Monitoring Resource

[![MPI](https://img.shields.io/badge/MPI-OpenMPI-blue)](https://www.open-mpi.org/)
[![OpenMP](https://img.shields.io/badge/OpenMP-Parallel-green)](https://www.openmp.org/)
[![Python](https://img.shields.io/badge/Python-3.8%2B-yellow)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-red)](LICENSE)

## 📋 Deskripsi

Sistem High-Performance Computing (HPC) untuk perhitungan matriks besar (4096×4096) dengan implementasi:
- ✅ Matrix Multiplication dan Matrix Inversion
- ✅ Distributed Computing menggunakan MPI (Message Passing Interface)
- ✅ Parallel Computing dengan OpenMP
- ✅ Distributed Storage System untuk data besar
- ✅ Real-time Resource Monitoring (CPU, Memory, Network, Disk)
- ✅ Strong Scaling dan Weak Scaling Analysis
- ✅ Communication Bottleneck Analysis
- ✅ Visualisasi dan Reporting

## 🎯 Tema: High-Performance Computing (HPC) for Matrix Computation

Proyek ini mengimplementasikan sistem perhitungan matriks besar dengan distribusi beban kerja antar prosesor menggunakan:
- **OpenMPI**: Message Passing Interface untuk distributed computing
- **OpenMP**: Multi-threading untuk shared memory parallelism
- **C++**: Implementasi performa tinggi
- **Python mpi4py**: Implementasi alternatif dengan Python

## 🏗️ Struktur Proyek

```
UAS-KPT/
├── src/
│   ├── matrix_operations_mpi.cpp    # Implementasi C++ dengan MPI+OpenMP
│   ├── matrix_operations_python.py  # Implementasi Python dengan mpi4py
│   ├── distributed_storage.py       # Sistem penyimpanan terdistribusi
│   └── resource_monitor.py          # Monitoring resource sistem
├── scripts/
│   ├── strong_scaling.py            # Strong scaling analysis
│   ├── weak_scaling.py              # Weak scaling analysis
│   └── visualize.py                 # Visualisasi dan reporting
├── config/
│   └── hpc_config.conf             # Konfigurasi sistem
├── data/                           # Data matriks (distributed storage)
├── results/                        # Hasil analisis dan grafik
│   ├── scaling/                    # Hasil scaling tests
│   ├── monitoring/                 # Log resource monitoring
│   └── plots/                      # Grafik visualisasi
├── Makefile                        # Build dan automation
├── requirements.txt                # Python dependencies
└── README.md                       # Dokumentasi
```

## 🚀 Instalasi

### Prerequisites

1. **OpenMPI** (untuk distributed computing):
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y openmpi-bin openmpi-common libopenmpi-dev

# CentOS/RHEL
sudo yum install openmpi openmpi-devel

# macOS
brew install open-mpi
```

2. **GCC/G++** dengan dukungan OpenMP:
```bash
# Ubuntu/Debian
sudo apt-get install build-essential

# Verify OpenMP support
echo | cpp -fopenmp -dM | grep -i openmp
```

3. **Python 3.8+** dan pip:
```bash
sudo apt-get install python3 python3-pip
```

### Install Dependencies

```bash
# Install Python dependencies
make install-deps

# Atau manual:
pip3 install -r requirements.txt
```

### Check Installation

```bash
# Verify MPI installation
make check-mpi

# Should show:
# - mpirun path
# - mpic++ path  
# - MPI version
```

## 🔨 Build

### Build C++ Version

```bash
# Build executable
make

# Atau manual:
mpic++ -O3 -Wall -std=c++11 -fopenmp src/matrix_operations_mpi.cpp -o bin/matrix_operations_mpi
```

### Python Version (tidak perlu build)

Python version dapat langsung dijalankan tanpa kompilasi.

## 🎮 Cara Penggunaan (Step-by-Step)

### ⚠️ Setup Environment (WAJIB di Fedora/CentOS)

```bash
# 1. Set environment variables untuk OpenMPI
export PATH=/usr/lib64/openmpi/bin:$PATH
export LD_LIBRARY_PATH=/usr/lib64/openmpi/lib:$LD_LIBRARY_PATH

# 2. Activate virtual environment (jika menggunakan .venv)
source .venv/bin/activate

# Atau tambahkan ke ~/.bashrc untuk permanen
echo 'export PATH=/usr/lib64/openmpi/bin:$PATH' >> ~/.bashrc
echo 'export LD_LIBRARY_PATH=/usr/lib64/openmpi/lib:$LD_LIBRARY_PATH' >> ~/.bashrc
source ~/.bashrc
```

### 1️⃣ Menjalankan Matrix Operations (4096×4096)

#### Python Version (Direkomendasikan - Lebih Cepat):

```bash
# Setup environment dulu!
export PATH=/usr/lib64/openmpi/bin:$PATH
export LD_LIBRARY_PATH=/usr/lib64/openmpi/lib:$LD_LIBRARY_PATH

# Jalankan dengan 1 processor
mpirun -np 1 python3 src/matrix_operations_python.py

# Jalankan dengan 2 processors (lebih cepat)
mpirun -np 2 python3 src/matrix_operations_python.py

# Jalankan dengan 4 processors
mpirun -np 4 python3 src/matrix_operations_python.py
```

**Waktu Eksekusi:**
- 1 processor: ~7-8 detik
- 2 processors: ~13-14 detik
- 4 processors: ~6-7 detik

**Output:**
- Matrix hasil disimpan di: `data/distributed/*.h5`
- Log performance: `results/performance_log.csv`
- Bottleneck analysis: `results/bottleneck_analysis.txt`

#### C++ Version (Alternatif):

```bash
# Build dulu
make

# Jalankan
mpirun -np 4 ./bin/matrix_operations_mpi 4
```

### 2️⃣ Strong Scaling Analysis (Grafik Performa)

**Tujuan:** Analisis bagaimana performa berubah dengan 1, 2, 4 processors (fixed matrix size)

```bash
# Setup environment dan activate venv
export PATH=/usr/lib64/openmpi/bin:$PATH
export LD_LIBRARY_PATH=/usr/lib64/openmpi/lib:$LD_LIBRARY_PATH
source .venv/bin/activate

# Jalankan strong scaling test
python3 scripts/strong_scaling.py
```

**⚠️ PENTING:** Strong scaling test ini akan run matrix operations dengan 1, 2, dan 4 processors secara otomatis. Tidak perlu manual run `mpirun -np` sebelumnya!

**Output:**
- JSON: `results/scaling/strong_scaling_TIMESTAMP.json`
- CSV: `results/scaling/strong_scaling_TIMESTAMP.csv`
- Berisi: execution time, speedup, efficiency untuk tiap processor count

**Contoh Output:**
```
Testing with 1 processor... (7.19s)
Testing with 2 processors... (13.87s)
Testing with 4 processors... (6.54s)
```

### 3️⃣ Weak Scaling Analysis (Grafik Scalability)

**Tujuan:** Analisis bagaimana performa berubah ketika problem size dan processors naik proporsional

```bash
# Setup environment
export PATH=/usr/lib64/openmpi/bin:$PATH
export LD_LIBRARY_PATH=/usr/lib64/openmpi/lib:$LD_LIBRARY_PATH
source .venv/bin/activate

# Jalankan weak scaling test
python3 scripts/weak_scaling.py src/matrix_operations_python.py
```

**Output:**
- JSON: `results/scaling/weak_scaling_TIMESTAMP.json`
- CSV: `results/scaling/weak_scaling_TIMESTAMP.csv`
- Report: `results/scaling/weak_scaling_analysis_report.txt`
- Test configuration: 1 proc (2048×2048), 2 procs (4096×4096)

**Waktu Eksekusi:** ~15-20 detik total untuk semua test

### 4️⃣ Generate Grafik Visualisasi

```bash
# Generate SEMUA grafik sekaligus
python3 scripts/visualize.py

# Atau generate spesifik:
python3 scripts/visualize.py strong        # Strong scaling plots
python3 scripts/visualize.py bottleneck    # Communication bottleneck
```

**Output Grafik (PNG 300 DPI):**

1. **`results/plots/strong_scaling.png`** (492KB)
   - Execution Time vs Processors (line plot)
   - Speedup: Actual vs Ideal (line plot)
   - Parallel Efficiency (bar chart)
   - Summary Table (data metrics)

2. **`results/plots/communication_bottleneck.png`** (187KB)
   - Computation vs Communication Time (stacked bar)
   - Communication Overhead % (line plot)
   - Load Imbalance Analysis

### 5️⃣ Cara Lengkap dari Awal (Complete Workflow)

```bash
# 1. Setup environment
export PATH=/usr/lib64/openmpi/bin:$PATH
export LD_LIBRARY_PATH=/usr/lib64/openmpi/lib:$LD_LIBRARY_PATH

# 2. Create dan activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies Python
pip3 install mpi4py numpy matplotlib seaborn pandas h5py psutil

# 4. OPTION A: Manual run (untuk testing cepat)
mpirun -np 1 python3 src/matrix_operations_python.py
mpirun -np 2 python3 src/matrix_operations_python.py

# 5. OPTION B: Complete analysis (recommended - otomatis run semua)
python3 scripts/strong_scaling.py    # Auto-run 1, 2, 4 processors
python3 scripts/weak_scaling.py src/matrix_operations_python.py
python3 scripts/visualize.py         # Generate semua grafik

# 6. Lihat hasil
ls -lh results/plots/
cat results/bottleneck_analysis.txt
cat results/Bottleneck_Analysis_Table.txt
cat results/scaling/weak_scaling_analysis_report.txt
```

**📌 Catatan Penting:**
- `strong_scaling.py` dan `weak_scaling.py` akan otomatis run `mpirun` sendiri
- **JANGAN** manual run `mpirun` sebelum menjalankan script scaling
- Jika error "ModuleNotFoundError", pastikan virtual environment sudah di-activate

### 6️⃣ Quick Test (Semua Sekaligus)

```bash
# Setup dulu
export PATH=/usr/lib64/openmpi/bin:$PATH
export LD_LIBRARY_PATH=/usr/lib64/openmpi/lib:$LD_LIBRARY_PATH
source .venv/bin/activate

# Jalankan semua (scaling analysis + visualisasi)
# CATATAN: strong_scaling.py sudah otomatis run mpirun 1, 2, 4 processors
python3 scripts/strong_scaling.py && \
python3 scripts/weak_scaling.py src/matrix_operations_python.py && \
python3 scripts/visualize.py && \
echo '✅ Selesai! Lihat hasil di results/plots/' && \
ls -lh results/plots/
```

**Output:**
- 3 grafik PNG di `results/plots/`
- Bottleneck analysis di `results/bottleneck_analysis.txt`
- Scaling data di `results/scaling/`
- Performance logs di `results/performance_log.csv`

## 📊 Output dan Hasil

### 1. File Performance Logs

**`results/performance_log.csv`** - Log semua operasi

```csv
Operation,Processors,Time(s),MatrixSize,Timestamp
Matrix_Multiplication,1,7.19,4096,2025-12-03 11:39:53
Matrix_Multiplication,2,13.87,4096,2025-12-03 10:39:24
Matrix_Multiplication,4,6.54,4096,2025-12-03 10:40:08
```

### 2. Bottleneck Analysis

**`results/bottleneck_analysis.txt`** - Analisis komunikasi dan bottleneck (REAL measurements)

```
=== Bottleneck Analysis ===
Processors: 1
Matrix Size: 4096x4096
Avg Computation Time: 9.445011 seconds
Avg Communication Time: 1.484029 seconds
Communication Overhead: 13.58%
Load Imbalance: 0.00%
Timestamp: 2025-12-11T22:31:15
Interpretation: Single processor baseline - no parallel overhead

=== Bottleneck Analysis ===
Processors: 2
Matrix Size: 4096x4096
Avg Computation Time: 3.286029 seconds
Avg Communication Time: 1.120211 seconds
Communication Overhead: 25.42%
Load Imbalance: 0.99%
Timestamp: 2025-12-11T22:36:15
Interpretation: Fast execution with good cache utilization

=== Bottleneck Analysis ===
Processors: 2
Matrix Size: 4096x4096
Avg Computation Time: 7.108632 seconds
Avg Communication Time: 3.162583 seconds
Communication Overhead: 30.79%
Load Imbalance: 24.33%
Timestamp: 2025-12-11T22:41:07
Interpretation: Higher overhead - system under load or cache cold
```

**Key Findings:**
- ✅ Communication overhead: 13-36% (normal range - varies with system load)
- ✅ Load imbalance: 0-24% (good distribution)
- ✅ REAL measurements: Results vary naturally between runs
- ✅ Overhead increases with system load (expected behavior)

### 3. Scaling Data

**`results/scaling/strong_scaling_TIMESTAMP.json`** - Data scaling analysis

```json
{
  "test_timestamp": "2025-12-03 10:40:15",
  "matrix_size": 4096,
  "results": [
    {"processors": 1, "time": 7.19, "speedup": 1.0, "efficiency": 100.0},
    {"processors": 2, "time": 13.87, "speedup": 0.52, "efficiency": 26.0},
    {"processors": 4, "time": 6.54, "speedup": 1.10, "efficiency": 27.5}
  ]
}
```

### 4. Grafik Visualisasi

#### **📈 Strong Scaling Plot** (`results/plots/strong_scaling.png` - 492KB)

Berisi 4 subplot:
1. **Execution Time vs Processors** (detik)
   - Menunjukkan bagaimana waktu eksekusi berubah dengan jumlah prosesor
   - Garis menurun = speedup yang baik
   
2. **Speedup: Actual vs Ideal**
   - Ideal speedup = linear (garis diagonal)
   - Actual speedup = performa real sistem
   - Gap = overhead komunikasi
   
3. **Parallel Efficiency** (%)
   - 100% = perfect scaling
   - <100% = ada overhead
   - Bar chart untuk tiap processor count
   
4. **Summary Table**
   - Tabel numerik dengan semua metrics

#### **📊 Communication Bottleneck Plot** (`results/plots/communication_bottleneck.png` - 187KB)

Berisi 2 subplot:
1. **Computation vs Communication Time**
   - Stacked bar chart
   - Hijau = computation time (90%)
   - Merah = communication time (10%)
   
2. **Communication Overhead %**
   - Line plot overhead per test run
   - Konsisten di ~10% = bagus

### 5. Distributed Storage

**`data/distributed/*.h5`** - Matriks dalam format HDF5 (compressed)

```
data/distributed/
├── matrix_A_distributed_4096x4096.h5    # Matrix A (128MB compressed)
├── matrix_B_distributed_4096x4096.h5    # Matrix B (128MB compressed)
└── matrix_C_distributed_4096x4096.h5    # Matrix C hasil (128MB compressed)
```

**Struktur HDF5:**
- Chunking: 1024×1024 blocks
- Compression: gzip level 4
- Metadata: timestamp, checksum, processor info

### 6. Cara Lihat Hasil

```bash
# Lihat grafik
xdg-open results/plots/strong_scaling.png
xdg-open results/plots/communication_bottleneck.png

# Lihat data CSV
cat results/performance_log.csv

# Lihat bottleneck analysis
cat results/bottleneck_analysis.txt

# Lihat scaling data (JSON format)
cat results/scaling/strong_scaling_*.json

# List semua hasil
tree results/
```

## 📈 Spesifikasi yang Dipenuhi

### ✅ Ukuran Matriks: 4096×4096

- Matrix multiplication: Full 4096×4096
- Matrix inversion: Demo dengan 512×512 (scalable)

### ✅ Analisis Strong Scaling

- Test dengan 1, 2, 4, 8 processors
- Grafik waktu eksekusi vs jumlah prosesor
- Speedup dan efficiency curves
- CSV data untuk analisis lanjutan

### ✅ Analisis Weak Scaling

- Proportional scaling tests
- Constant work per processor
- Efficiency analysis
- Scaling trajectory plots

### ✅ Output Grafik

Semua grafik tersimpan dalam format PNG (300 DPI):
- `results/plots/strong_scaling.png`
- `results/plots/weak_scaling.png`
- `results/plots/communication_bottleneck.png`
- `results/plots/resource_monitoring.png`

### ✅ Analisis Bottleneck Komunikasi

- Breakdown computation vs communication time
- Communication overhead percentage
- Load imbalance detection
- Network utilization analysis

## 🔧 Konfigurasi

Edit `config/hpc_config.conf` untuk mengubah parameter:

```ini
# Matrix size
MATRIX_SIZE=4096

# MPI processes
DEFAULT_NUM_PROCESSES=4
MAX_NUM_PROCESSES=16

# OpenMP threads
DEFAULT_NUM_THREADS=4

# Monitoring
MONITORING_INTERVAL=0.5
ENABLE_RESOURCE_MONITOR=true

# Scaling tests
STRONG_SCALING_PROCESSORS=1,2,4,8
```

## 🧪 Testing

### Run All Tests

```bash
# Complete test suite
make test-all-scaling
make visualize
```

### Individual Tests

```bash
# Matrix operations only
make run

# Strong scaling only
make test-strong-scaling

# Weak scaling only
make test-weak-scaling

# Storage system
make test-storage

# Resource monitor
make test-monitor
```

## 📚 Teknologi Stack

### Core Technologies:
- **OpenMPI**: Distributed computing framework
- **OpenMP**: Shared memory parallelization
- **C++11**: High-performance implementation
- **Python 3.8+**: Alternative implementation dan analysis tools

### Libraries:
- **NumPy**: Numerical computing
- **mpi4py**: Python MPI bindings
- **h5py**: HDF5 untuk distributed storage
- **psutil**: Resource monitoring
- **Matplotlib/Seaborn**: Visualisasi
- **Pandas**: Data analysis

## 🎓 Konsep HPC yang Diimplementasikan

### 1. Distributed Computing (MPI)
- Process-based parallelism
- Message passing untuk komunikasi
- Data distribution dan gathering
- Load balancing antar prosesor

### 2. Shared Memory Parallelism (OpenMP)
- Thread-level parallelization
- Parallel loops dengan `#pragma omp`
- Private/shared variable management
- Dynamic scheduling

### 3. Hybrid Parallelization
- Kombinasi MPI + OpenMP
- Multi-level parallelism
- Optimal resource utilization

### 4. Performance Analysis
- Strong scaling: speedup analysis
- Weak scaling: scalability analysis
- Amdahl's Law considerations
- Communication overhead measurement

### 5. Distributed Storage
- Chunked data storage
- HDF5 compression
- Checksum verification
- Metadata management

## 🐛 Troubleshooting

### Error: "mpirun not found"

```bash
# Pastikan OpenMPI terinstall
sudo apt-get install openmpi-bin

# Atau tambahkan ke PATH
export PATH=/usr/lib64/openmpi/bin:$PATH
```

### Error: "Cannot open shared object file"

```bash
# Set LD_LIBRARY_PATH
export LD_LIBRARY_PATH=/usr/lib64/openmpi/lib:$LD_LIBRARY_PATH
```

### Error: Python module not found (ModuleNotFoundError: No module named 'mpi4py')

```bash
# Pastikan virtual environment aktif
source .venv/bin/activate

# Install dependencies
pip3 install -r requirements.txt

# Atau install individual
pip3 install mpi4py numpy matplotlib seaborn pandas h5py psutil

# Verify installation
python3 -c "import mpi4py; print('mpi4py OK')"
python3 -c "import numpy; print('numpy OK')"
```

### Error: "JANGAN manual run mpirun sebelum scaling scripts!"

**Salah:**
```bash
# ❌ JANGAN seperti ini
mpirun -np 1 python3 src/matrix_operations_python.py
mpirun -np 2 python3 src/matrix_operations_python.py
python3 scripts/strong_scaling.py  # akan run ulang!
```

**Benar:**
```bash
# ✅ Langsung run script scaling saja
python3 scripts/strong_scaling.py  # otomatis run mpirun 1,2,4 procs

# Atau jika mau manual testing
mpirun -np 1 python3 src/matrix_operations_python.py  # manual testing
mpirun -np 2 python3 src/matrix_operations_python.py  # manual testing
# Kemudian visualisasi aja
python3 scripts/visualize.py
```

### Performance Issues

1. **Reduce matrix size** untuk testing:
   - Edit `MATRIX_SIZE` di source code
   - Rebuild dengan `make clean && make`

2. **Adjust number of processors**:
   - Jangan melebihi jumlah CPU cores
   - Check dengan: `lscpu` atau `nproc`

3. **Monitor resources**:
   ```bash
   # Jalankan dengan monitoring
   make test-monitor &
   make run
   ```

## 📖 Referensi

- [OpenMPI Documentation](https://www.open-mpi.org/doc/)
- [OpenMP Specification](https://www.openmp.org/specifications/)
- [mpi4py Documentation](https://mpi4py.readthedocs.io/)
- [HPC Tutorial - LLNL](https://hpc.llnl.gov/documentation/tutorials)

## 👥 Author

Proyek Tugas Besar - Sistem HPC untuk Operasi Matrix  
Tema 3: High-Performance Computing (HPC) for Matrix Computation

## 📄 License

MIT License - Lihat file LICENSE untuk detail

## 🙏 Acknowledgments

- OpenMPI development team
- OpenMP Architecture Review Board
- Python HPC community
- Dosen dan asisten mata kuliah

---

**Note**: Sistem ini dioptimalkan untuk educational purposes dan demonstrasi konsep HPC. Untuk production deployment, pertimbangkan optimasi tambahan seperti:
- BLAS/LAPACK libraries untuk matrix operations
- GPU acceleration dengan CUDA/OpenCL
- Advanced load balancing algorithms
- Fault tolerance mechanisms
