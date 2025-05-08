import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from sklearn.preprocessing import StandardScaler
import joblib
import os
from typing import Tuple, Dict, Any

from app.model.data_processor import DataProcessor

class DriverBehaviorModel:
    def __init__(self, model_path: str = 'app/model/trained_models/driver_model.pkl'):
        """Initialize the driver behavior model."""
        self.model_path = model_path
        self.model = None
        self.scaler = None
        self.data_processor = DataProcessor()
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
    
    def train(self, train_data_path: str) -> Dict[str, Any]:
        """Train the model using the provided training data."""
        # Load and preprocess training data
        train_data = pd.read_csv(train_data_path)
        processed_data = self.data_processor.preprocess_data(train_data)
        
        # Extract features
        features_df = self.data_processor.extract_features(processed_data)
        
        if features_df.empty:
            return {"error": "Failed to extract features from training data"}
        
        # Prepare features and target
        X = features_df.drop(['Timestamp'], axis=1, errors='ignore')
        
        # If Class column exists in original data, map it to the features
        if 'Class' in processed_data.columns:
            # For each feature window, get the most common class in that window
            y = []
            window_size = self.data_processor.window_size
            overlap = self.data_processor.overlap
            
            for i in range(0, len(processed_data) - window_size + 1, window_size - overlap):
                window = processed_data.iloc[i:i + window_size]
                if len(window) < window_size:
                    continue
                
                # Get most common class in this window
                class_counts = window['Class'].value_counts()
                most_common_class = class_counts.index[0] if not class_counts.empty else 'UNKNOWN'
                y.append(most_common_class)
            
            # Ensure X and y have the same length
            if len(y) != len(X):
                # Truncate the longer one
                min_len = min(len(X), len(y))
                X = X.iloc[:min_len]
                y = y[:min_len]
        else:
            return {"error": "Training data does not contain Class labels"}
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate model
        y_pred = self.model.predict(X_test_scaled)
        accuracy = accuracy_score(y_test, y_pred)
        report = classification_report(y_test, y_pred, output_dict=True)
        
        # Save model
        joblib.dump(self.model, self.model_path)
        
        # Save scaler
        scaler_path = os.path.join(os.path.dirname(self.model_path), 'scaler.pkl')
        joblib.dump(self.scaler, scaler_path)
        
        return {
            "accuracy": accuracy,
            "classification_report": report,
            "model_path": self.model_path
        }
    
    def load(self) -> bool:
        """Load the trained model from disk."""
        try:
            if os.path.exists(self.model_path):
                self.model = joblib.load(self.model_path)
                
                # Load scaler if it exists
                scaler_path = os.path.join(os.path.dirname(self.model_path), 'scaler.pkl')
                if os.path.exists(scaler_path):
                    self.scaler = joblib.load(scaler_path)
                
                return True
            return False
        except Exception as e:
            print(f"Error loading model: {e}")
            return False
    
    def evaluate(self, test_data_path: str) -> Dict[str, Any]:
        """Evaluate the model using test data."""
        if self.model is None:
            if not self.load():
                return {"error": "Model not loaded"}
        
        # Load and preprocess test data
        test_data = pd.read_csv(test_data_path)
        processed_data = self.data_processor.preprocess_data(test_data)
        
        # Extract features
        features_df = self.data_processor.extract_features(processed_data)
        
        if features_df.empty:
            return {"error": "Failed to extract features from test data"}
        
        # Prepare features and target
        X = features_df.drop(['Timestamp'], axis=1, errors='ignore')
        
        # If Class column exists in original data, map it to the features
        if 'Class' in processed_data.columns:
            # For each feature window, get the most common class in that window
            y = []
            window_size = self.data_processor.window_size
            overlap = self.data_processor.overlap
            
            for i in range(0, len(processed_data) - window_size + 1, window_size - overlap):
                window = processed_data.iloc[i:i + window_size]
                if len(window) < window_size:
                    continue
                
                # Get most common class in this window
                class_counts = window['Class'].value_counts()
                most_common_class = class_counts.index[0] if not class_counts.empty else 'UNKNOWN'
                y.append(most_common_class)
            
            # Ensure X and y have the same length
            if len(y) != len(X):
                # Truncate the longer one
                min_len = min(len(X), len(y))
                X = X.iloc[:min_len]
                y = y[:min_len]
        else:
            return {"error": "Test data does not contain Class labels"}
        
        # Scale features if scaler exists
        if self.scaler is not None:
            X_scaled = self.scaler.transform(X)
        else:
            X_scaled = X
        
        # Make predictions
        y_pred = self.model.predict(X_scaled)
        
        # Evaluate
        accuracy = accuracy_score(y, y_pred)
        report = classification_report(y, y_pred, output_dict=True)
        
        return {
            "accuracy": accuracy,
            "classification_report": report
        }
