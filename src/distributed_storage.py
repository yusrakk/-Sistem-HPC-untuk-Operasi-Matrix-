#!/usr/bin/env python3
"""
Distributed Storage Manager for HPC Matrix Operations
Handles storage, retrieval, and management of large matrices across distributed systems
"""

import os
import json
import numpy as np
import h5py
from datetime import datetime
from pathlib import Path
import hashlib

class DistributedStorageManager:
    """
    Manages distributed storage for large matrices
    Supports chunked storage, compression, and metadata tracking
    """
    
    def __init__(self, storage_dir="data/distributed", compression="gzip"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.compression = compression
        self.metadata_file = self.storage_dir / "storage_metadata.json"
        self.metadata = self._load_metadata()
        
    def _load_metadata(self):
        """Load metadata from disk"""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
        return {"matrices": {}}
    
    def _save_metadata(self):
        """Save metadata to disk"""
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)
    
    def _compute_checksum(self, data):
        """Compute checksum for data integrity"""
        return hashlib.sha256(data.tobytes()).hexdigest()
    
    def save_matrix(self, matrix, name, chunk_size=1024, compress=True):
        """
        Save matrix to distributed storage with chunking
        
        Args:
            matrix: numpy array to save
            name: unique identifier for the matrix
            chunk_size: size of chunks for distributed storage
            compress: whether to use compression
        """
        matrix_dir = self.storage_dir / name
        matrix_dir.mkdir(exist_ok=True)
        
        # Save using HDF5 for efficient storage
        h5_file = matrix_dir / f"{name}.h5"
        
        with h5py.File(h5_file, 'w') as f:
            if compress:
                dset = f.create_dataset(
                    'matrix', 
                    data=matrix,
                    compression=self.compression,
                    compression_opts=4,
                    chunks=(min(chunk_size, matrix.shape[0]), 
                           min(chunk_size, matrix.shape[1]))
                )
            else:
                dset = f.create_dataset('matrix', data=matrix)
            
            # Add attributes
            dset.attrs['shape'] = matrix.shape
            dset.attrs['dtype'] = str(matrix.dtype)
            dset.attrs['timestamp'] = datetime.now().isoformat()
        
        # Update metadata
        self.metadata["matrices"][name] = {
            "path": str(h5_file),
            "shape": matrix.shape,
            "dtype": str(matrix.dtype),
            "size_mb": matrix.nbytes / (1024**2),
            "compressed": compress,
            "checksum": self._compute_checksum(matrix),
            "timestamp": datetime.now().isoformat()
        }
        self._save_metadata()
        
        print(f"[Storage] Saved matrix '{name}' ({matrix.shape}) to {h5_file}")
        return str(h5_file)
    
    def load_matrix(self, name, verify_checksum=True):
        """
        Load matrix from distributed storage
        
        Args:
            name: identifier of the matrix
            verify_checksum: whether to verify data integrity
        """
        if name not in self.metadata["matrices"]:
            raise ValueError(f"Matrix '{name}' not found in storage")
        
        info = self.metadata["matrices"][name]
        h5_file = Path(info["path"])
        
        if not h5_file.exists():
            raise FileNotFoundError(f"Storage file not found: {h5_file}")
        
        with h5py.File(h5_file, 'r') as f:
            matrix = f['matrix'][:]
        
        # Verify checksum
        if verify_checksum:
            checksum = self._compute_checksum(matrix)
            if checksum != info["checksum"]:
                raise ValueError(f"Checksum mismatch for matrix '{name}'")
        
        print(f"[Storage] Loaded matrix '{name}' ({matrix.shape}) from {h5_file}")
        return matrix
    
    def save_matrix_distributed(self, matrix, name, num_parts=4):
        """
        Save matrix in multiple parts for distributed storage
        
        Args:
            matrix: numpy array to save
            name: unique identifier
            num_parts: number of parts to split into
        """
        matrix_dir = self.storage_dir / name
        matrix_dir.mkdir(exist_ok=True)
        
        rows_per_part = matrix.shape[0] // num_parts
        parts_info = []
        
        for i in range(num_parts):
            start_row = i * rows_per_part
            end_row = matrix.shape[0] if i == num_parts - 1 else (i + 1) * rows_per_part
            
            part_matrix = matrix[start_row:end_row, :]
            part_file = matrix_dir / f"{name}_part{i}.npy"
            
            np.save(part_file, part_matrix)
            
            parts_info.append({
                "part_id": i,
                "path": str(part_file),
                "rows": [start_row, end_row],
                "shape": part_matrix.shape,
                "size_mb": part_matrix.nbytes / (1024**2)
            })
        
        # Save metadata
        self.metadata["matrices"][name] = {
            "type": "distributed",
            "shape": matrix.shape,
            "dtype": str(matrix.dtype),
            "num_parts": num_parts,
            "parts": parts_info,
            "checksum": self._compute_checksum(matrix),
            "timestamp": datetime.now().isoformat()
        }
        self._save_metadata()
        
        print(f"[Storage] Saved matrix '{name}' in {num_parts} parts")
        return parts_info
    
    def load_matrix_distributed(self, name, verify_checksum=True):
        """
        Load matrix from distributed parts
        
        Args:
            name: identifier of the matrix
            verify_checksum: whether to verify data integrity
        """
        if name not in self.metadata["matrices"]:
            raise ValueError(f"Matrix '{name}' not found in storage")
        
        info = self.metadata["matrices"][name]
        
        if info.get("type") != "distributed":
            raise ValueError(f"Matrix '{name}' is not stored in distributed format")
        
        # Load all parts
        parts = []
        for part_info in info["parts"]:
            part_file = Path(part_info["path"])
            if not part_file.exists():
                raise FileNotFoundError(f"Part file not found: {part_file}")
            parts.append(np.load(part_file))
        
        # Concatenate parts
        matrix = np.vstack(parts)
        
        # Verify checksum
        if verify_checksum:
            checksum = self._compute_checksum(matrix)
            if checksum != info["checksum"]:
                raise ValueError(f"Checksum mismatch for matrix '{name}'")
        
        print(f"[Storage] Loaded distributed matrix '{name}' ({matrix.shape})")
        return matrix
    
    def list_matrices(self):
        """List all stored matrices"""
        print("\n" + "="*60)
        print("Stored Matrices")
        print("="*60)
        
        for name, info in self.metadata["matrices"].items():
            print(f"\nName: {name}")
            print(f"  Shape: {info['shape']}")
            print(f"  Type: {info.get('type', 'single')}")
            print(f"  Size: {info.get('size_mb', 0):.2f} MB")
            print(f"  Timestamp: {info['timestamp']}")
            
            if info.get('type') == 'distributed':
                print(f"  Parts: {info['num_parts']}")
        
        print("="*60)
        return self.metadata["matrices"]
    
    def delete_matrix(self, name):
        """Delete matrix from storage"""
        if name not in self.metadata["matrices"]:
            raise ValueError(f"Matrix '{name}' not found")
        
        info = self.metadata["matrices"][name]
        
        # Delete files
        if info.get("type") == "distributed":
            for part_info in info["parts"]:
                part_file = Path(part_info["path"])
                if part_file.exists():
                    part_file.unlink()
        else:
            h5_file = Path(info["path"])
            if h5_file.exists():
                h5_file.unlink()
        
        # Remove from metadata
        del self.metadata["matrices"][name]
        self._save_metadata()
        
        print(f"[Storage] Deleted matrix '{name}'")
    
    def get_storage_stats(self):
        """Get storage statistics"""
        total_size = 0
        num_matrices = len(self.metadata["matrices"])
        
        for info in self.metadata["matrices"].values():
            total_size += info.get("size_mb", 0)
        
        stats = {
            "total_matrices": num_matrices,
            "total_size_mb": total_size,
            "storage_dir": str(self.storage_dir),
            "compression": self.compression
        }
        
        return stats


def main():
    """Test distributed storage manager"""
    print("Testing Distributed Storage Manager...")
    
    storage = DistributedStorageManager()
    
    # Create test matrix
    print("\n[1] Creating test matrix...")
    test_matrix = np.random.rand(4096, 4096)
    
    # Save as single file
    print("\n[2] Saving as single compressed file...")
    storage.save_matrix(test_matrix, "test_matrix_single", compress=True)
    
    # Save as distributed parts
    print("\n[3] Saving as distributed parts...")
    storage.save_matrix_distributed(test_matrix, "test_matrix_distributed", num_parts=4)
    
    # List matrices
    print("\n[4] Listing stored matrices...")
    storage.list_matrices()
    
    # Load matrix
    print("\n[5] Loading matrices...")
    loaded_single = storage.load_matrix("test_matrix_single")
    loaded_distributed = storage.load_matrix_distributed("test_matrix_distributed")
    
    # Verify
    print("\n[6] Verifying data integrity...")
    assert np.allclose(test_matrix, loaded_single), "Single file verification failed"
    assert np.allclose(test_matrix, loaded_distributed), "Distributed file verification failed"
    print("✓ Data integrity verified")
    
    # Storage stats
    print("\n[7] Storage statistics:")
    stats = storage.get_storage_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
