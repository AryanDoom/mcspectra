import os
import time
import hashlib
import json
from datetime import datetime
try:
    from pymongo import MongoClient
    MONGO_AVAILABLE = True
except ImportError:
    MONGO_AVAILABLE = False
    print("pymongo not installed, using mock database.")

try:
    import numpy as np
    from sklearn.ensemble import RandomForestClassifier
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("scikit-learn or numpy not installed. AI classification will use mock logic.")

"""
TODO LIST (Implementation Plan):
[x] Step 1: File Scanner - Extract metadata (size, access time, path).
[x] Step 2: Queue Processing - Manage files to be analyzed.
[x] Step 3: Metadata Storage - Store file details (MongoDB/Mock DB).
[x] Step 4: Hashing and Deduplication - SHA-256 content-based deduplication.
[x] Step 5: AI Classification - ML model to classify file importance.
[x] Step 6: Decision Layer - Apply labels (Important, Redundant, Uncertain).
[x] Step 7: Garbage Collection - Safely mark for deletion or move to trash.
[x] Step 8: Reporting - Summarize storage recovered and operations performed.
"""

class StorageOptimizer:
    def __init__(self, target_directory, db_uri="mongodb://localhost:27017/", trash_dir="./trash"):
        """
        Initializes the AI-Assisted Storage Optimization System.
        """
        self.target_directory = target_directory
        self.trash_dir = trash_dir
        self.queue = []
        self.model = self._initialize_ai_model()
        
        # Ensure trash directory exists
        if not os.path.exists(self.trash_dir):
            os.makedirs(self.trash_dir)

        # Database connection
        if MONGO_AVAILABLE:
            self.client = MongoClient(db_uri)
            self.db = self.client['storage_optimization']
            self.metadata_collection = self.db['files']
        else:
            # Mock DB for demonstration
            self.mock_db = {}
            
    def _initialize_ai_model(self):
        """
        Initializes and returns a machine learning model for file classification.
        In a real scenario, this would load a pre-trained model.
        """
        if SKLEARN_AVAILABLE:
            # A dummy Random Forest classifier for demonstration
            model = RandomForestClassifier()
            # X_train: [days_since_access, file_size_mb, access_frequency]
            # y_train: 0 (Redundant), 1 (Important), 2 (Uncertain)
            X_train = np.array([[300, 50, 1], [2, 10, 50], [100, 500, 5], [400, 1, 0]])
            y_train = np.array([0, 1, 2, 0])
            model.fit(X_train, y_train)
            return model
        return None

    # --- Step 1: File Scanner ---
    def scan_directory(self):
        """
        Scans the target directory recursively to gather file paths.
        Adds found files to the processing queue.
        """
        print(f"Scanning directory: {self.target_directory}")
        for root, _, files in os.walk(self.target_directory):
            for file in files:
                file_path = os.path.join(root, file)
                self.queue.append(file_path)
        print(f"Discovered {len(self.queue)} files.")

    # --- Step 4: Hashing and Deduplication ---
    def compute_file_hash(self, file_path):
        """
        Computes the SHA-256 hash of a file for deduplication.
        Reads in chunks to handle large files.
        """
        sha256_hash = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception as e:
            print(f"Error hashing {file_path}: {e}")
            return None

    # --- Step 5 & 6: AI Classification & Decision Layer ---
    def classify_file(self, metadata):
        """
        Uses heuristics or the ML model to decide if a file is Important, Redundant, or Uncertain.
        """
        current_time = time.time()
        days_since_access = (current_time - metadata['last_access']) / (24 * 3600)
        size_mb = metadata['size'] / (1024 * 1024)
        
        # Heuristic/Mock values for access frequency (this would ideally be tracked over time)
        access_frequency = 1 
        
        if self.model and SKLEARN_AVAILABLE:
            features = np.array([[days_since_access, size_mb, access_frequency]])
            prediction = self.model.predict(features)[0]
            labels = {0: "Redundant", 1: "Important", 2: "Uncertain"}
            return labels.get(prediction, "Uncertain")
        else:
            # Fallback heuristic if ML is unavailable
            if days_since_access > 180: # 6 months unused
                return "Redundant"
            elif days_since_access < 30:
                return "Important"
            return "Uncertain"

    # --- Step 2 & 3: Queue Processing and Metadata Storage ---
    def process_queue(self):
        """
        Processes each file in the queue: Extracts metadata, computes hash, handles deduplication, and applies AI classification.
        """
        print("Processing queue...")
        while self.queue:
            file_path = self.queue.pop(0)
            if not os.path.exists(file_path):
                continue
                
            try:
                # Extract Metadata
                stat = os.stat(file_path)
                file_hash = self.compute_file_hash(file_path)
                
                metadata = {
                    "path": file_path,
                    "size": stat.st_size,
                    "last_access": stat.st_atime,
                    "hash": file_hash,
                    "timestamp": datetime.now().isoformat()
                }
                
                # Check Deduplication
                is_duplicate = False
                if MONGO_AVAILABLE:
                    existing_file = self.metadata_collection.find_one({"hash": file_hash})
                    if existing_file and existing_file["path"] != file_path:
                        is_duplicate = True
                else:
                    if file_hash in self.mock_db:
                        is_duplicate = True
                
                # Classification
                classification = self.classify_file(metadata)
                metadata["classification"] = classification
                metadata["is_duplicate"] = is_duplicate
                
                # Store Metadata
                if MONGO_AVAILABLE:
                    self.metadata_collection.update_one({"path": file_path}, {"$set": metadata}, upsert=True)
                else:
                    self.mock_db[file_hash] = metadata
                
                print(f"Processed: {os.path.basename(file_path)} | Class: {classification} | Duplicate: {is_duplicate}")
                
            except Exception as e:
                print(f"Failed to process {file_path}: {e}")

    # --- Step 7: Garbage Collection ---
    def garbage_collection(self):
        """
        Finds all redundant and duplicate files and moves them to trash.
        """
        print("Running Garbage Collection...")
        reclaimed_bytes = 0
        deleted_count = 0
        
        # Determine files to remove (Mock DB logic implemented here for demonstration readiness)
        files_to_remove = []
        if MONGO_AVAILABLE:
            candidates = self.metadata_collection.find({"$or": [{"classification": "Redundant"}, {"is_duplicate": True}]})
            files_to_remove = list(candidates)
        else:
            for v in self.mock_db.values():
                if v.get("classification") == "Redundant" or v.get("is_duplicate") == True:
                    files_to_remove.append(v)
        
        for file_meta in files_to_remove:
            path = file_meta.get("path")
            if path and os.path.exists(path):
                try:
                    # Move to trash instead of hard delete
                    filename = os.path.basename(path)
                    new_path = os.path.join(self.trash_dir, filename)
                    os.rename(path, new_path)
                    
                    reclaimed_bytes += file_meta.get("size", 0)
                    deleted_count += 1
                    
                    # Update DB
                    if MONGO_AVAILABLE:
                        self.metadata_collection.delete_one({"path": path})
                        
                except Exception as e:
                    print(f"Could not GC file {path}: {e}")
                    
        return deleted_count, reclaimed_bytes

    # --- Step 8: Reporting ---
    def generate_report(self, deleted_count, reclaimed_bytes):
        """
        Generates a summary report of the actions taken.
        """
        mb_saved = reclaimed_bytes / (1024 * 1024)
        report = f"\n--- Optimization Report ---\n"
        report += f"Files Handled/Trashed: {deleted_count}\n"
        report += f"Storage Reclaimed: {mb_saved:.2f} MB\n"
        report += f"Time: {datetime.now().isoformat()}\n"
        report += "-"*27
        print(report)
        return report

    def run_full_pipeline(self):
        """
        Orchestrates the complete optimization workflow.
        """
        print("Starting AI-Assisted Storage Optimization Pipeline...")
        self.scan_directory()
        self.process_queue()
        deleted_count, reclaimed_bytes = self.garbage_collection()
        self.generate_report(deleted_count, reclaimed_bytes)
        print("Pipeline execution completed.")


if __name__ == "__main__":
    # Ensure sample execution
    # For testing, we optimization against a dummy directory
    dummy_target = "./test_storage"
    if not os.path.exists(dummy_target):
        os.makedirs(dummy_target)
        # Create dummy files
        with open(os.path.join(dummy_target, "test1.txt"), "w") as f: f.write("Hello World! This is an active file.")
        with open(os.path.join(dummy_target, "test1_duplicate.txt"), "w") as f: f.write("Hello World! This is an active file.") # duplicate

    optimizer = StorageOptimizer(target_directory=dummy_target)
    optimizer.run_full_pipeline()
    
