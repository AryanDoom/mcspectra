import time

try:
    import numpy as np
    from sklearn.ensemble import RandomForestClassifier
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("scikit-learn not installed. AI classifier will use backup rules.")

class AIClassifier:
    """
    Evaluates file metadata to determine if it is Important, Redundant, or Uncertain.
    Uses Machine Learning if available, else uses fallback heuristics.
    """
    def __init__(self):
        self.model = self._initialize_model()

    def _initialize_model(self):
        """
        Mocks training a simple Random Forest.
        In reality, this logic would load `.pkl` weights from a pre-trained model.
        """
        if SKLEARN_AVAILABLE:
            model = RandomForestClassifier()
            # X_train features: [days_since_access, file_size_mb, access_frequency]
            # y_train labels: 0 (Redundant), 1 (Important), 2 (Uncertain)
            X_train = np.array([
                [300, 50, 1],   # Old, large -> Redundant
                [2, 10, 50],    # New, heavily accessed -> Important
                [100, 500, 5],  # Medium age, huge -> Uncertain
                [400, 1, 0]     # Very old, small -> Redundant
            ])
            y_train = np.array([0, 1, 2, 0])
            model.fit(X_train, y_train)
            return model
        return None

    def classify(self, metadata):
        """
        Returns a string classification label based on the file metadata.
        """
        current_time = time.time()
        
        # Calculate days since access
        last_access = metadata.get('last_access', current_time)
        days_since_access = (current_time - last_access) / (24 * 3600)
        
        # Size in MB (fallback to 0 if size key is missing)
        size_mb = metadata.get('size', 0) / (1024 * 1024)
        
        # Access frequency mocked for this prototype
        access_frequency = 1 

        if self.model and SKLEARN_AVAILABLE:
            features = np.array([[days_since_access, size_mb, access_frequency]])
            prediction = self.model.predict(features)[0]
            
            labels = {0: "Redundant", 1: "Important", 2: "Uncertain"}
            return labels.get(prediction, "Uncertain")
        else:
            # Fallback Logic
            if days_since_access > 180:   # older than ~6 months
                return "Redundant"
            elif days_since_access < 30:  # accessed in last 30 days
                return "Important"
            return "Uncertain"
