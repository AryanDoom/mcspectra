import os
import hashlib
from datetime import datetime

class FileScanner:
    """
    Handles directory traversal, metadata extraction, and content hashing.
    """
    def __init__(self, target_directory):
        self.target_directory = target_directory
        self.queue = []

    def scan_directory(self):
        """
        Recursively scans the target directory and populates the file queue.
        """
        print(f"Scanning directory: {self.target_directory}")
        for root, _, files in os.walk(self.target_directory):
            for file in files:
                file_path = os.path.join(root, file)
                self.queue.append(file_path)
        print(f"Discovered {len(self.queue)} files.")
        return self.queue

    def compute_file_hash(self, file_path):
        """
        Computes the SHA-256 hash of a file for content-based deduplication.
        Handles large files by reading in chunks.
        """
        sha256_hash = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                # Read file in 4MB chunks
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception as e:
            print(f"Error computing hash for {file_path}: {e}")
            return None

    def extract_metadata(self, file_path):
        """
        Extracts foundational metadata (size, access time) for a given file.
        """
        try:
            stat = os.stat(file_path)
            file_hash = self.compute_file_hash(file_path)
            
            metadata = {
                "path": file_path,
                "size": stat.st_size,
                "last_access": stat.st_atime,
                "hash": file_hash,
                "timestamp": datetime.now().isoformat()
            }
            return metadata
        except Exception as e:
            print(f"Failed to extract metadata for {file_path}: {e}")
            return None
