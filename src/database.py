try:
    from pymongo import MongoClient
    MONGO_AVAILABLE = True
except ImportError:
    MONGO_AVAILABLE = False
    print("pymongo not installed, using memory mock database.")

class DatabaseManager:
    """
    Handles connections to MongoDB and operations related to file metadata.
    Includes a fallback in-memory mock if MongoDB is unavailable.
    """
    def __init__(self, db_uri="mongodb://localhost:27017/"):
        if MONGO_AVAILABLE:
            self.client = MongoClient(db_uri)
            self.db = self.client['storage_optimization']
            self.collection = self.db['files']
            self.mock_db = None
        else:
            self.client = None
            self.collection = None
            self.mock_db = {}

    def insert_or_update(self, metadata):
        """
        Inserts new metadata or updates it if the file path already exists.
        """
        file_path = metadata.get("path")
        if MONGO_AVAILABLE:
            self.collection.update_one(
                {"path": file_path}, 
                {"$set": metadata}, 
                upsert=True
            )
        else:
            # For the mock DB, we can just key by the file hash or path
            self.mock_db[file_path] = metadata

    def check_duplicate_hash(self, file_hash, file_path):
        """
        Checks if a file with the same hash already exists, to flag duplicates.
        """
        if MONGO_AVAILABLE:
            existing = self.collection.find_one({"hash": file_hash})
            if existing and existing["path"] != file_path:
                return True
            return False
        else:
            # Check mock db
            for path, meta in self.mock_db.items():
                if meta.get("hash") == file_hash and path != file_path:
                    return True
            return False

    def get_removable_files(self):
        """
        Returns a list of file metadata dictionaries that are marked Redundant or are Duplicates.
        """
        if MONGO_AVAILABLE:
            candidates = self.collection.find(
                {"$or": [{"classification": "Redundant"}, {"is_duplicate": True}]}
            )
            return list(candidates)
        else:
            candidates = []
            for meta in self.mock_db.values():
                if meta.get("classification") == "Redundant" or meta.get("is_duplicate") == True:
                    candidates.append(meta)
            return candidates

    def remove_file_record(self, file_path):
        """
        Removes a single file's metadata from the database.
        """
        if MONGO_AVAILABLE:
            self.collection.delete_one({"path": file_path})
        else:
            if file_path in self.mock_db:
                del self.mock_db[file_path]
