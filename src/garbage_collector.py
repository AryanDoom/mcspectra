import os

class GarbageCollector:
    """
    Handles safe deletion by moving flagged files to a temporary trash location.
    """
    def __init__(self, trash_dir="./trash"):
        self.trash_dir = trash_dir
        if not os.path.exists(self.trash_dir):
            os.makedirs(self.trash_dir)

    def collect(self, files_to_remove):
        """
        Takes a list of file metadata records, moves them to the trash,
        and returns metrics about reclaimed space.
        """
        print(f"Running Garbage Collection on {len(files_to_remove)} items...")
        reclaimed_bytes = 0
        deleted_count = 0
        removed_paths = []

        for file_meta in files_to_remove:
            path = file_meta.get("path")
            if path and os.path.exists(path):
                try:
                    filename = os.path.basename(path)
                    new_path = os.path.join(self.trash_dir, filename)
                    # Move to trash
                    os.rename(path, new_path)
                    
                    reclaimed_bytes += file_meta.get("size", 0)
                    deleted_count += 1
                    removed_paths.append(path)
                except Exception as e:
                    print(f"Could not garbage collect file {path}: {e}")
                    
        return deleted_count, reclaimed_bytes, removed_paths
