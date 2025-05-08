import pandas as pd
import numpy as np
from scipy import stats
import joblib
import os
from typing import Dict, List, Tuple, Any

class DataProcessor:
    def __init__(self, model_path: str = 'app/model/trained_models/driver_model.pkl'):
        """Initialize the data processor with the trained model."""
        self.model_path = model_path
        self.model = self._load_model() if os.path.exists(model_path) else None
        self.window_size = 50  # Number of data points to consider for a window
        self.overlap = 25      # Overlap between consecutive windows
        
    def _load_model(self):
        """Load the trained model from disk."""
        try:
            return joblib.load(self.model_path)
        except Exception as e:
            print(f"Error loading model: {e}")
            return None
    
    def preprocess_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """Preprocess the raw motion data."""
        # Handle missing values
        data = data.fillna(method='ffill').fillna(method='bfill')
        
        # Sort by timestamp
        if 'Timestamp' in data.columns:
            data = data.sort_values('Timestamp')
        
        # Convert data types
        numeric_cols = ['AccX', 'AccY', 'AccZ', 'GyroX', 'GyroY', 'GyroZ']
        for col in numeric_cols:
            if col in data.columns:
                data[col] = pd.to_numeric(data[col], errors='coerce')
        
        return data
    
    def extract_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Extract features from preprocessed data."""
        features = []
        
        # Process data in windows with overlap
        for i in range(0, len(data) - self.window_size + 1, self.window_size - self.overlap):
            window = data.iloc[i:i + self.window_size]
            
            # Skip windows that are too small
            if len(window) < self.window_size:
                continue
                
            window_features = {}
            
            # Time-domain features for each axis
            for col in ['AccX', 'AccY', 'AccZ', 'GyroX', 'GyroY', 'GyroZ']:
                if col in window.columns:
                    values = window[col].values
                    window_features[f'{col}_mean'] = np.mean(values)
                    window_features[f'{col}_std'] = np.std(values)
                    window_features[f'{col}_max'] = np.max(values)
                    window_features[f'{col}_min'] = np.min(values)
                    window_features[f'{col}_range'] = np.max(values) - np.min(values)
                    window_features[f'{col}_median'] = np.median(values)
                    window_features[f'{col}_kurtosis'] = stats.kurtosis(values)
                    window_features[f'{col}_skew'] = stats.skew(values)
                    
                    # Zero crossings
                    zero_crossings = np.where(np.diff(np.signbit(values)))[0]
                    window_features[f'{col}_zero_crossings'] = len(zero_crossings)
                    
                    # Peak-to-peak
                    window_features[f'{col}_p2p'] = np.max(values) - np.min(values)
            
            # Magnitude features
            if all(col in window.columns for col in ['AccX', 'AccY', 'AccZ']):
                acc_mag = np.sqrt(window['AccX']**2 + window['AccY']**2 + window['AccZ']**2)
                window_features['Acc_mag_mean'] = np.mean(acc_mag)
                window_features['Acc_mag_std'] = np.std(acc_mag)
                window_features['Acc_mag_max'] = np.max(acc_mag)
                
            if all(col in window.columns for col in ['GyroX', 'GyroY', 'GyroZ']):
                gyro_mag = np.sqrt(window['GyroX']**2 + window['GyroY']**2 + window['GyroZ']**2)
                window_features['Gyro_mag_mean'] = np.mean(gyro_mag)
                window_features['Gyro_mag_std'] = np.std(gyro_mag)
                window_features['Gyro_mag_max'] = np.max(gyro_mag)
            
            # Add window timestamp (middle of window)
            if 'Timestamp' in window.columns:
                window_features['Timestamp'] = window['Timestamp'].iloc[len(window) // 2]
            
            features.append(window_features)
        
        return pd.DataFrame(features) if features else pd.DataFrame()
    
    def detect_events(self, data: pd.DataFrame) -> Dict[str, List[Dict[str, Any]]]:
        """Detect driving events from the data."""
        events = {
            'harsh_acceleration': [],
            'harsh_braking': [],
            'harsh_cornering': [],
            'phone_usage': [],
            'speeding': []
        }
        
        # Thresholds for event detection
        acc_threshold = 0.5  # m/s²
        brake_threshold = -0.5  # m/s²
        corner_threshold = 0.4  # rad/s
        
        # Process data in windows
        for i in range(0, len(data) - self.window_size + 1, self.window_size - self.overlap):
            window = data.iloc[i:i + self.window_size]
            
            # Skip windows that are too small
            if len(window) < self.window_size:
                continue
                
            timestamp = window['Timestamp'].iloc[len(window) // 2] if 'Timestamp' in window.columns else i
            
            # Harsh acceleration detection
            if 'AccX' in window.columns and window['AccX'].max() > acc_threshold:
                events['harsh_acceleration'].append({
                    'timestamp': timestamp,
                    'value': window['AccX'].max(),
                    'duration': self.window_size
                })
            
            # Harsh braking detection
            if 'AccX' in window.columns and window['AccX'].min() < brake_threshold:
                events['harsh_braking'].append({
                    'timestamp': timestamp,
                    'value': window['AccX'].min(),
                    'duration': self.window_size
                })
            
            # Harsh cornering detection
            if 'GyroZ' in window.columns and (window['GyroZ'].max() > corner_threshold or window['GyroZ'].min() < -corner_threshold):
                events['harsh_cornering'].append({
                    'timestamp': timestamp,
                    'value': window['GyroZ'].max() if abs(window['GyroZ'].max()) > abs(window['GyroZ'].min()) else window['GyroZ'].min(),
                    'duration': self.window_size
                })
            
            # Phone usage detection (high frequency vibrations)
            if all(col in window.columns for col in ['AccX', 'AccY', 'AccZ']):
                # Calculate jerk (derivative of acceleration)
                jerk_x = np.diff(window['AccX'].values)
                jerk_y = np.diff(window['AccY'].values)
                jerk_z = np.diff(window['AccZ'].values)
                
                # High frequency components indicate potential phone usage
                if (np.std(jerk_x) > 0.2 and np.std(jerk_y) > 0.2 and np.std(jerk_z) > 0.2):
                    events['phone_usage'].append({
                        'timestamp': timestamp,
                        'value': np.std(jerk_x) + np.std(jerk_y) + np.std(jerk_z),
                        'duration': self.window_size
                    })
        
        return events
    
    def predict_behavior(self, features: pd.DataFrame) -> List[str]:
        """Predict driving behavior using the trained model."""
        if self.model is None:
            return ['UNKNOWN'] * len(features)
        
        # Select only the features used during training
        model_features = self.model.feature_names_in_ if hasattr(self.model, 'feature_names_in_') else None
        
        if model_features is not None:
            # Keep only the features that exist in both the model and the current features
            common_features = [f for f in model_features if f in features.columns]
            if not common_features:
                return ['UNKNOWN'] * len(features)
            
            X = features[common_features]
        else:
            # If we don't know the model features, use all except Timestamp
            X = features.drop(['Timestamp'], axis=1, errors='ignore')
        
        try:
            return self.model.predict(X)
        except Exception as e:
            print(f"Prediction error: {e}")
            return ['UNKNOWN'] * len(features)
    
    def calculate_scores(self, data: pd.DataFrame, events: Dict[str, List[Dict[str, Any]]]) -> Dict[str, float]:
        """Calculate driver scores based on data and detected events."""
        scores = {
            'overall': 0.0,
            'acceleration': 0.0,
            'braking': 0.0,
            'cornering': 0.0,
            'phone_usage': 0.0,
            'consistency': 0.0
        }
        
        # Base score
        base_score = 100
        
        # Penalties for events
        acc_penalty = 5 * len(events['harsh_acceleration'])
        brake_penalty = 5 * len(events['harsh_braking'])
        corner_penalty = 5 * len(events['harsh_cornering'])
        phone_penalty = 10 * len(events['phone_usage'])
        
        # Calculate individual scores
        scores['acceleration'] = max(0, 100 - acc_penalty)
        scores['braking'] = max(0, 100 - brake_penalty)
        scores['cornering'] = max(0, 100 - corner_penalty)
        scores['phone_usage'] = max(0, 100 - phone_penalty)
        
        # Calculate consistency score based on standard deviation of acceleration
        if 'AccX' in data.columns and 'AccY' in data.columns and 'AccZ' in data.columns:
            acc_std = np.mean([np.std(data['AccX']), np.std(data['AccY']), np.std(data['AccZ'])])
            # Lower std deviation means more consistent driving
            consistency_score = 100 * np.exp(-acc_std)
            scores['consistency'] = min(100, max(0, consistency_score))
        else:
            scores['consistency'] = 50  # Default if data is missing
        
        # Calculate overall score (weighted average)
        weights = {
            'acceleration': 0.2,
            'braking': 0.2,
            'cornering': 0.2,
            'phone_usage': 0.3,
            'consistency': 0.1
        }
        
        scores['overall'] = sum(scores[key] * weights[key] for key in weights)
        
        # Round scores to 1 decimal place
        for key in scores:
            scores[key] = round(scores[key], 1)
        
        return scores
    
    def process_trip_data(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Process trip data and return comprehensive analysis."""
        # Preprocess data
        processed_data = self.preprocess_data(data)
        
        # Extract features
        features = self.extract_features(processed_data)
        
        # Detect events
        events = self.detect_events(processed_data)
        
        # Calculate scores
        scores = self.calculate_scores(processed_data, events)
        
        # Predict behaviors if model is available
        behaviors = []
        if self.model is not None and not features.empty:
            behaviors = self.predict_behavior(features)
        
        # Calculate trip statistics
        stats = {
            'trip_duration': (processed_data['Timestamp'].max() - processed_data['Timestamp'].min()) / 1000 if 'Timestamp' in processed_data.columns else 0,
            'data_points': len(processed_data),
            'event_count': sum(len(events[e]) for e in events),
            'behavior_distribution': {}
        }
        
        # Calculate behavior distribution
        if behaviors:
            behavior_counts = {}
            for behavior in behaviors:
                behavior_counts[behavior] = behavior_counts.get(behavior, 0) + 1
            
            for behavior, count in behavior_counts.items():
                stats['behavior_distribution'][behavior] = count / len(behaviors)
        
        return {
            'scores': scores,
            'events': events,
            'statistics': stats
        }
    
    def process_realtime_data(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Process a chunk of real-time data and return immediate feedback."""
        # Preprocess data
        processed_data = self.preprocess_data(data)
        
        # Extract features
        features = self.extract_features(processed_data)
        
        # Detect events
        events = self.detect_events(processed_data)
        
        # Calculate preliminary scores based on this chunk
        scores = self.calculate_scores(processed_data, events)
        
        # Predict current behavior if model is available
        current_behavior = 'UNKNOWN'
        if self.model is not None and not features.empty:
            behaviors = self.predict_behavior(features)
            if behaviors:
                # Get the most common behavior in this chunk
                behavior_counts = {}
                for behavior in behaviors:
                    behavior_counts[behavior] = behavior_counts.get(behavior, 0) + 1
                
                current_behavior = max(behavior_counts.items(), key=lambda x: x[1])[0]
        
        return {
            'current_scores': scores,
            'current_events': events,
            'current_behavior': current_behavior
        }
