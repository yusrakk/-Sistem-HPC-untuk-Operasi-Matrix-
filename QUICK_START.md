# 🚀 QUICK START GUIDE - Sistem HPC Matrix 4096×4096

## ⚡ Cara Cepat Running (5 Menit)

### 1️⃣ Setup Environment (Sekali Saja)

```bash
cd /home/yusa/UAS-KPT

# Set environment OpenMPI
export PATH=/usr/lib64/openmpi/bin:$PATH
export LD_LIBRARY_PATH=/usr/lib64/openmpi/lib:$LD_LIBRARY_PATH

# Install Python dependencies
pip3 install mpi4py numpy matplotlib seaborn pandas h5py psutil
```

### 2️⃣ Jalankan Matrix Operations

```bash
# Test dengan 1 processor (~7 detik)
mpirun -np 1 python3 src/matrix_operations_python.py

# Test dengan 2 processors (~14 detik)
mpirun -np 2 python3 src/matrix_operations_python.py
```

✅ **Output:**
- Data matrix: `data/distributed/*.h5`
- Performance log: `results/performance_log.csv`
- Bottleneck analysis: `results/bottleneck_analysis.txt`

### 3️⃣ Generate Grafik

```bash
# Generate SEMUA grafik
python3 scripts/visualize.py
```

✅ **Output Grafik:**
- `results/plots/strong_scaling.png` (492KB)
- `results/plots/communication_bottleneck.png` (187KB)

### 4️⃣ Lihat Hasil

```bash
# Buka grafik
xdg-open results/plots/strong_scaling.png
xdg-open results/plots/communication_bottleneck.png

# Lihat bottleneck analysis
cat results/bottleneck_analysis.txt

# Lihat performance log
cat results/performance_log.csv
```

---

## 📊 Ringkasan Hasil (4096×4096)

| Processors | Time (s) | Speedup | Efficiency | Comm Overhead |
|-----------|----------|---------|------------|---------------|
| 1         | 7.19     | 1.0×    | 100%       | 10%           |
| 2         | 13.87    | 0.52×   | 26%        | 10%           |
| 4         | 6.54     | 1.10×   | 28%        | 10%           |

**Key Metrics:**
- ✅ Communication Overhead: 10% (excellent)
- ✅ Load Imbalance: 0% (perfect)
- ✅ Matrix Size: 4096×4096 (16.8M elements)
- ✅ Memory per Matrix: 134 MB

---

## 🎯 Lengkap dengan Scaling Analysis

```bash
# Setup environment
export PATH=/usr/lib64/openmpi/bin:$PATH
export LD_LIBRARY_PATH=/usr/lib64/openmpi/lib:$LD_LIBRARY_PATH

# 1. Run matrix operations dengan berbagai processor
mpirun -np 1 python3 src/matrix_operations_python.py
mpirun -np 2 python3 src/matrix_operations_python.py

# 2. Run strong scaling analysis
python3 scripts/strong_scaling.py

# 3. Generate visualisasi
python3 scripts/visualize.py

# 4. Lihat hasil
cat results/bottleneck_analysis.txt
ls -lh results/plots/
```

---

## 📂 Struktur Output

```
results/
├── performance_log.csv              # Log semua operasi
├── bottleneck_analysis.txt          # Analisis komunikasi
├── scaling/
│   ├── strong_scaling_*.json       # Data scaling (JSON)
│   └── strong_scaling_*.csv        # Data scaling (CSV)
└── plots/
    ├── strong_scaling.png          # Grafik performa (492KB)
    └── communication_bottleneck.png # Grafik bottleneck (187KB)

data/distributed/
├── matrix_A_distributed_4096x4096.h5  # Matrix A (128MB)
├── matrix_B_distributed_4096x4096.h5  # Matrix B (128MB)
└── matrix_C_distributed_4096x4096.h5  # Matrix C hasil (128MB)
```

---

## ⚠️ Troubleshooting

### Error: "mpirun not found"
```bash
export PATH=/usr/lib64/openmpi/bin:$PATH
```

### Error: "libmpi.so: cannot open shared object"
```bash
export LD_LIBRARY_PATH=/usr/lib64/openmpi/lib:$LD_LIBRARY_PATH
```

### Error: Python module not found
```bash
pip3 install mpi4py numpy matplotlib seaborn pandas h5py psutil
```

---

## 📖 Dokumentasi Lengkap

Lihat `README.md` untuk dokumentasi detail tentang:
- Instalasi prerequisites
- Penjelasan komponen sistem
- Konfigurasi advanced
- Referensi teknis

