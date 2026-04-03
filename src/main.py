import os
from datetime import datetime
from flask import Flask, send_from_directory, jsonify

from scanner import FileScanner
from database import DatabaseManager
from ai_classifier import AIClassifier
from garbage_collector import GarbageCollector

class StorageOptimizationPipeline:
    def __init__(self, target_directory):
        self.target_directory = target_directory
        self.scanner = FileScanner(target_directory)
        self.db = DatabaseManager()
        self.classifier = AIClassifier()
        self.gc = GarbageCollector()

    def run(self):
        print("Starting AI-Assisted Storage Optimization Pipeline...")
        
        # 1. Scan directory
        queue = self.scanner.scan_directory()
        
        # 2. Process Files
        print("Processing files and classifying...")
        for file_path in queue:
            if not os.path.exists(file_path):
                continue
                
            metadata = self.scanner.extract_metadata(file_path)
            if not metadata:
                continue
                
            # Check for duplicates using hash
            is_dup = self.db.check_duplicate_hash(metadata["hash"], metadata["path"])
            metadata["is_duplicate"] = is_dup
            
            # AI Classification
            classification = self.classifier.classify(metadata)
            metadata["classification"] = classification
            
            # Save to Database
            self.db.insert_or_update(metadata)
            
            print(f"Processed: {os.path.basename(file_path)} | Class: {classification} | Dup: {is_dup}")
            
        # 3. Garbage Collection
        removable_files = self.db.get_removable_files()
        deleted_count, reclaimed_bytes, removed_paths = self.gc.collect(removable_files)
        
        # Cleanup DB
        for path in removed_paths:
            self.db.remove_file_record(path)
            
        # 4. Reporting
        self.generate_report(deleted_count, reclaimed_bytes)
        print("Pipeline execution completed.")
        
    def generate_report(self, deleted_count, reclaimed_bytes):
        mb_saved = reclaimed_bytes / (1024 * 1024)
        report = f"\n--- Optimization Report ---\n"
        report += f"Files Handled/Trashed: {deleted_count}\n"
        report += f"Storage Reclaimed: {mb_saved:.2f} MB\n"
        report += f"Time: {datetime.now().isoformat()}\n"
        report += "-"*27
        print(report)

app = Flask(__name__)
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

@app.route("/")
def index():
    return send_from_directory(ROOT_DIR, "index.html")

@app.route("/<path:path>")
def serve_assets(path):
    return send_from_directory(ROOT_DIR, path)

@app.route("/api/run_pipeline", methods=["POST"])
def api_run_pipeline():
    dummy_target = os.path.join(ROOT_DIR, "test_storage")
    if not os.path.exists(dummy_target):
        os.makedirs(dummy_target)
        # Seed test data
        with open(os.path.join(dummy_target, "test1.txt"), "w") as f: f.write("Hello World! This is an active file.")
        with open(os.path.join(dummy_target, "test1_duplicate.txt"), "w") as f: f.write("Hello World! This is an active file.")
        
    pipeline = StorageOptimizationPipeline(target_directory=dummy_target)
    pipeline.run()
    return jsonify({"status": "success", "message": "Pipeline completed"})

if __name__ == "__main__":
    print(f"Starting Flask App. Root frontend directory: {ROOT_DIR}")
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)
