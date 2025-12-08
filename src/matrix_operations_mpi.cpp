/**
 * Matrix Operations with MPI and OpenMP
 * High-Performance Computing for 4096x4096 Matrix
 * 
 * Operations: Matrix Multiplication and Matrix Inversion
 * Technologies: OpenMPI, OpenMP, C++
 */

#include <mpi.h>
#include <omp.h>
#include <iostream>
#include <fstream>
#include <vector>
#include <cmath>
#include <cstdlib>
#include <ctime>
#include <iomanip>
#include <chrono>
#include <string>
#include <sstream>

using namespace std;
using namespace std::chrono;

const int MATRIX_SIZE = 4096;

class ResourceMonitor {
private:
    double start_time;
    double end_time;
    string operation_name;
    
public:
    ResourceMonitor(string op_name) : operation_name(op_name) {
        start_time = MPI_Wtime();
    }
    
    double stop() {
        end_time = MPI_Wtime();
        return end_time - start_time;
    }
    
    void log_metrics(int rank, int size, double elapsed_time, const string& filename) {
        if (rank == 0) {
            ofstream logfile(filename, ios::app);
            logfile << operation_name << "," 
                    << size << "," 
                    << elapsed_time << "," 
                    << MATRIX_SIZE << endl;
            logfile.close();
        }
    }
};

// Initialize matrix with random values
void initialize_matrix(double* matrix, int rows, int cols) {
    #pragma omp parallel for collapse(2)
    for (int i = 0; i < rows; i++) {
        for (int j = 0; j < cols; j++) {
            matrix[i * cols + j] = (double)(rand() % 100) / 10.0;
        }
    }
}

// Initialize identity matrix
void initialize_identity(double* matrix, int size) {
    #pragma omp parallel for collapse(2)
    for (int i = 0; i < size; i++) {
        for (int j = 0; j < size; j++) {
            matrix[i * size + j] = (i == j) ? 1.0 : 0.0;
        }
    }
}

// Matrix multiplication using MPI + OpenMP
void matrix_multiply_mpi(double* A, double* B, double* C, 
                         int rank, int size, int n) {
    
    int rows_per_proc = n / size;
    int start_row = rank * rows_per_proc;
    int end_row = (rank == size - 1) ? n : start_row + rows_per_proc;
    
    // Local computation with OpenMP
    #pragma omp parallel for collapse(2)
    for (int i = start_row; i < end_row; i++) {
        for (int j = 0; j < n; j++) {
            double sum = 0.0;
            for (int k = 0; k < n; k++) {
                sum += A[i * n + k] * B[k * n + j];
            }
            C[i * n + j] = sum;
        }
    }
    
    // Gather results
    if (rank == 0) {
        for (int p = 1; p < size; p++) {
            int p_start = p * rows_per_proc;
            int p_end = (p == size - 1) ? n : p_start + rows_per_proc;
            int count = (p_end - p_start) * n;
            
            MPI_Recv(&C[p_start * n], count, MPI_DOUBLE, p, 0, 
                     MPI_COMM_WORLD, MPI_STATUS_IGNORE);
        }
    } else {
        int count = (end_row - start_row) * n;
        MPI_Send(&C[start_row * n], count, MPI_DOUBLE, 0, 0, MPI_COMM_WORLD);
    }
}

// Gauss-Jordan elimination for matrix inversion (distributed)
void matrix_inverse_mpi(double* A, double* A_inv, int rank, int size, int n) {
    
    // Copy A to working matrix
    double* work = new double[n * n];
    #pragma omp parallel for
    for (int i = 0; i < n * n; i++) {
        work[i] = A[i];
    }
    
    initialize_identity(A_inv, n);
    
    // Distribute rows among processors
    int rows_per_proc = n / size;
    
    for (int col = 0; col < n; col++) {
        // Find pivot
        int pivot_row = col;
        double max_val = fabs(work[col * n + col]);
        
        for (int i = col + 1; i < n; i++) {
            if (fabs(work[i * n + col]) > max_val) {
                max_val = fabs(work[i * n + col]);
                pivot_row = i;
            }
        }
        
        // Swap rows if needed
        if (pivot_row != col) {
            for (int j = 0; j < n; j++) {
                swap(work[col * n + j], work[pivot_row * n + j]);
                swap(A_inv[col * n + j], A_inv[pivot_row * n + j]);
            }
        }
        
        // Scale pivot row
        double pivot = work[col * n + col];
        if (fabs(pivot) < 1e-10) {
            cout << "Matrix is singular!" << endl;
            delete[] work;
            return;
        }
        
        #pragma omp parallel for
        for (int j = 0; j < n; j++) {
            work[col * n + j] /= pivot;
            A_inv[col * n + j] /= pivot;
        }
        
        // Eliminate column (distributed among processes)
        int start_row = rank * rows_per_proc;
        int end_row = (rank == size - 1) ? n : start_row + rows_per_proc;
        
        #pragma omp parallel for
        for (int i = start_row; i < end_row; i++) {
            if (i != col) {
                double factor = work[i * n + col];
                for (int j = 0; j < n; j++) {
                    work[i * n + j] -= factor * work[col * n + j];
                    A_inv[i * n + j] -= factor * A_inv[col * n + j];
                }
            }
        }
        
        // Synchronize work and A_inv matrices
        MPI_Allgather(MPI_IN_PLACE, 0, MPI_DATATYPE_NULL,
                      work, n * rows_per_proc, MPI_DOUBLE, MPI_COMM_WORLD);
        MPI_Allgather(MPI_IN_PLACE, 0, MPI_DATATYPE_NULL,
                      A_inv, n * rows_per_proc, MPI_DOUBLE, MPI_COMM_WORLD);
    }
    
    delete[] work;
}

// Save matrix to distributed storage
void save_matrix_distributed(double* matrix, int n, const string& filename, 
                             int rank, int size) {
    int rows_per_proc = n / size;
    int start_row = rank * rows_per_proc;
    int end_row = (rank == size - 1) ? n : start_row + rows_per_proc;
    
    stringstream ss;
    ss << filename << "_part" << rank << ".dat";
    
    ofstream file(ss.str(), ios::binary);
    if (file.is_open()) {
        for (int i = start_row; i < end_row; i++) {
            file.write(reinterpret_cast<char*>(&matrix[i * n]), n * sizeof(double));
        }
        file.close();
    }
}

// Load matrix from distributed storage
void load_matrix_distributed(double* matrix, int n, const string& filename,
                             int rank, int size) {
    int rows_per_proc = n / size;
    int start_row = rank * rows_per_proc;
    int end_row = (rank == size - 1) ? n : start_row + rows_per_proc;
    
    stringstream ss;
    ss << filename << "_part" << rank << ".dat";
    
    ifstream file(ss.str(), ios::binary);
    if (file.is_open()) {
        for (int i = start_row; i < end_row; i++) {
            file.read(reinterpret_cast<char*>(&matrix[i * n]), n * sizeof(double));
        }
        file.close();
    }
}

// Analyze communication bottleneck
void analyze_communication(int rank, int size, double comp_time, 
                          double comm_time, const string& filename) {
    double total_comp_time, total_comm_time;
    
    MPI_Reduce(&comp_time, &total_comp_time, 1, MPI_DOUBLE, MPI_SUM, 0, MPI_COMM_WORLD);
    MPI_Reduce(&comm_time, &total_comm_time, 1, MPI_DOUBLE, MPI_SUM, 0, MPI_COMM_WORLD);
    
    if (rank == 0) {
        double avg_comp = total_comp_time / size;
        double avg_comm = total_comm_time / size;
        double comm_ratio = (avg_comm / (avg_comp + avg_comm)) * 100;
        
        ofstream logfile(filename, ios::app);
        logfile << "Processors: " << size << endl;
        logfile << "Avg Computation Time: " << avg_comp << " seconds" << endl;
        logfile << "Avg Communication Time: " << avg_comm << " seconds" << endl;
        logfile << "Communication Overhead: " << comm_ratio << "%" << endl;
        logfile << "---" << endl;
        logfile.close();
    }
}

int main(int argc, char** argv) {
    MPI_Init(&argc, &argv);
    
    int rank, size;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);
    
    // Set number of OpenMP threads
    int num_threads = 4;
    if (argc > 1) {
        num_threads = atoi(argv[1]);
    }
    omp_set_num_threads(num_threads);
    
    srand(time(NULL) + rank);
    
    // Allocate matrices
    double* A = new double[MATRIX_SIZE * MATRIX_SIZE];
    double* B = new double[MATRIX_SIZE * MATRIX_SIZE];
    double* C = new double[MATRIX_SIZE * MATRIX_SIZE];
    double* A_inv = new double[MATRIX_SIZE * MATRIX_SIZE];
    
    if (rank == 0) {
        cout << "=== HPC Matrix Operations System ===" << endl;
        cout << "Matrix Size: " << MATRIX_SIZE << "x" << MATRIX_SIZE << endl;
        cout << "MPI Processes: " << size << endl;
        cout << "OpenMP Threads per Process: " << num_threads << endl;
        cout << "Total Parallel Units: " << size * num_threads << endl;
        cout << "====================================" << endl;
    }
    
    // Initialize matrices
    initialize_matrix(A, MATRIX_SIZE, MATRIX_SIZE);
    initialize_matrix(B, MATRIX_SIZE, MATRIX_SIZE);
    
    MPI_Barrier(MPI_COMM_WORLD);
    
    // ===== MATRIX MULTIPLICATION =====
    if (rank == 0) {
        cout << "\n[1] Starting Matrix Multiplication..." << endl;
    }
    
    ResourceMonitor mult_monitor("Matrix_Multiplication");
    double mult_start = MPI_Wtime();
    
    matrix_multiply_mpi(A, B, C, rank, size, MATRIX_SIZE);
    
    MPI_Barrier(MPI_COMM_WORLD);
    double mult_time = mult_monitor.stop();
    double mult_comm = MPI_Wtime() - mult_start - mult_time;
    
    if (rank == 0) {
        cout << "   Completed in " << mult_time << " seconds" << endl;
        mult_monitor.log_metrics(rank, size, mult_time, 
                                "results/performance_log.csv");
    }
    
    // Save result to distributed storage
    save_matrix_distributed(C, MATRIX_SIZE, "data/matrix_C", rank, size);
    
    MPI_Barrier(MPI_COMM_WORLD);
    
    // ===== MATRIX INVERSION =====
    if (rank == 0) {
        cout << "\n[2] Starting Matrix Inversion..." << endl;
    }
    
    // Use a smaller test matrix for inversion (512x512) due to computational cost
    int inv_size = 512;
    double* A_small = new double[inv_size * inv_size];
    double* A_small_inv = new double[inv_size * inv_size];
    
    initialize_matrix(A_small, inv_size, inv_size);
    
    ResourceMonitor inv_monitor("Matrix_Inversion");
    double inv_start = MPI_Wtime();
    
    matrix_inverse_mpi(A_small, A_small_inv, rank, size, inv_size);
    
    MPI_Barrier(MPI_COMM_WORLD);
    double inv_time = inv_monitor.stop();
    double inv_comm = MPI_Wtime() - inv_start - inv_time;
    
    if (rank == 0) {
        cout << "   Completed in " << inv_time << " seconds" << endl;
        inv_monitor.log_metrics(rank, size, inv_time, 
                               "results/performance_log.csv");
    }
    
    // Analyze communication bottleneck
    analyze_communication(rank, size, mult_time, mult_comm, 
                         "results/bottleneck_analysis.txt");
    
    if (rank == 0) {
        cout << "\n=== Execution Summary ===" << endl;
        cout << "Matrix Multiplication: " << mult_time << " seconds" << endl;
        cout << "Matrix Inversion (" << inv_size << "x" << inv_size << "): " 
             << inv_time << " seconds" << endl;
        cout << "Results saved to distributed storage" << endl;
        cout << "Performance logs: results/performance_log.csv" << endl;
        cout << "Bottleneck analysis: results/bottleneck_analysis.txt" << endl;
    }
    
    // Cleanup
    delete[] A;
    delete[] B;
    delete[] C;
    delete[] A_inv;
    delete[] A_small;
    delete[] A_small_inv;
    
    MPI_Finalize();
    return 0;
}
