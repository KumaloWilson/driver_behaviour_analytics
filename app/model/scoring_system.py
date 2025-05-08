from typing import Dict, List, Any
import numpy as np
import pandas as pd

class ScoringSystem:
    def __init__(self):
        """Initialize the scoring system with default weights."""
        # Weights for different components of the overall score
        self.weights = {
            'acceleration': 0.2,
            'braking': 0.2,
            'cornering': 0.2,
            'phone_usage': 0.3,
            'consistency': 0.1
        }
        
        # Thresholds for event severity
        self.thresholds = {
            'harsh_acceleration': {
                'mild': 0.3,
                'moderate': 0.5,
                'severe': 0.7
            },
            'harsh_braking': {
                'mild': -0.3,
                'moderate': -0.5,
                'severe': -0.7
            },
            'harsh_cornering': {
                'mild': 0.3,
                'moderate': 0.5,
                'severe': 0.7
            }
        }
        
        # Penalties for different event types
        self.penalties = {
            'harsh_acceleration': {
                'mild': 2,
                'moderate': 5,
                'severe': 10
            },
            'harsh_braking': {
                'mild': 2,
                'moderate': 5,
                'severe': 10
            },
            'harsh_cornering': {
                'mild': 2,
                'moderate': 5,
                'severe': 10
            },
            'phone_usage': 10,
            'speeding': 8
        }
    
    def _get_event_severity(self, event_type: str, value: float) -> str:
        """Determine the severity of an event based on its value."""
        if event_type not in self.thresholds:
            return 'unknown'
        
        thresholds = self.thresholds[event_type]
        
        # For braking (negative values)
        if event_type == 'harsh_braking':
            if value <= thresholds['severe']:
                return 'severe'
            elif value <= thresholds['moderate']:
                return 'moderate'
            elif value <= thresholds['mild']:
                return 'mild'
            return 'normal'
        
        # For acceleration and cornering (positive values)
        if value >= thresholds['severe']:
            return 'severe'
        elif value >= thresholds['moderate']:
            return 'moderate'
        elif value >= thresholds['mild']:
            return 'mild'
        return 'normal'
    
    def _calculate_event_penalties(self, events: Dict[str, List[Dict[str, Any]]]) -> Dict[str, float]:
        """Calculate penalties for each type of event."""
        penalties = {
            'acceleration': 0,
            'braking': 0,
            'cornering': 0,
            'phone_usage': 0,
            'speeding': 0
        }
        
        # Process harsh acceleration events
        for event in events.get('harsh_acceleration', []):
            severity = self._get_event_severity('harsh_acceleration', event['value'])
            if severity in self.penalties['harsh_acceleration']:
                penalties['acceleration'] += self.penalties['harsh_acceleration'][severity]
        
        # Process harsh braking events
        for event in events.get('harsh_braking', []):
            severity = self._get_event_severity('harsh_braking', event['value'])
            if severity in self.penalties['harsh_braking']:
                penalties['braking'] += self.penalties['harsh_braking'][severity]
        
        # Process harsh cornering events
        for event in events.get('harsh_cornering', []):
            severity = self._get_event_severity('harsh_cornering', abs(event['value']))
            if severity in self.penalties['harsh_cornering']:
                penalties['cornering'] += self.penalties['harsh_cornering'][severity]
        
        # Process phone usage events
        penalties['phone_usage'] = len(events.get('phone_usage', [])) * self.penalties['phone_usage']
        
        # Process speeding events
        penalties['speeding'] = len(events.get('speeding', [])) * self.penalties['speeding']
        
        return penalties
    
    def _calculate_consistency_score(self, data: pd.DataFrame) -> float:
        """Calculate a score for driving consistency."""
        if 'AccX' not in data.columns or 'AccY' not in data.columns or 'AccZ' not in data.columns:
            return 50.0  # Default if data is missing
        
        # Calculate standard deviation of acceleration
        acc_std = np.mean([np.std(data['AccX']), np.std(data['AccY']), np.std(data['AccZ'])])
        
        # Lower std deviation means more consistent driving
        # Use an exponential function to map std deviation to a score between 0 and 100
        consistency_score = 100 * np.exp(-2 * acc_std)
        
        return min(100, max(0, consistency_score))
    
    def calculate_trip_scores(self, data: pd.DataFrame, events: Dict[str, List[Dict[str, Any]]]) -> Dict[str, float]:
        """Calculate comprehensive scores for a completed trip."""
        # Base score for each category
        base_score = 100.0
        
        # Calculate penalties for events
        penalties = self._calculate_event_penalties(events)
        
        # Calculate individual scores
        scores = {
            'acceleration': max(0, base_score - penalties['acceleration']),
            'braking': max(0, base_score - penalties['braking']),
            'cornering': max(0, base_score - penalties['cornering']),
            'phone_usage': max(0, base_score - penalties['phone_usage']),
            'speeding': max(0, base_score - penalties['speeding']),
            'consistency': self._calculate_consistency_score(data)
        }
        
        # Calculate overall score (weighted average)
        overall_score = 0.0
        total_weight = 0.0
        
        for category, weight in self.weights.items():
            if category in scores:
                overall_score += scores[category] * weight
                total_weight += weight
        
        # Normalize by total weight
        if total_weight > 0:
            overall_score /= total_weight
        
        scores['overall'] = overall_score
        
        # Round scores to 1 decimal place
        for key in scores:
            scores[key] = round(scores[key], 1)
        
        return scores
    
    def calculate_realtime_score(self, data_chunk: pd.DataFrame, events_chunk: Dict[str, List[Dict[str, Any]]]) -> Dict[str, float]:
        """Calculate a preliminary score for a chunk of real-time data."""
        # Use the same algorithm as for trip scores, but with potentially less data
        return self.calculate_trip_scores(data_chunk, events_chunk)
    
    def generate_feedback(self, scores: Dict[str, float], events: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Generate actionable feedback based on scores and events."""
        feedback = {
            'summary': '',
            'strengths': [],
            'areas_for_improvement': [],
            'tips': []
        }
        
        # Generate summary
        if scores['overall'] >= 90:
            feedback['summary'] = "Excellent driving! You demonstrated safe and efficient driving behavior."
        elif scores['overall'] >= 80:
            feedback['summary'] = "Very good driving. You showed good control with a few areas for improvement."
        elif scores['overall'] >= 70:
            feedback['summary'] = "Good driving with some areas that need attention."
        elif scores['overall'] >= 60:
            feedback['summary'] = "Average driving with several areas that need improvement."
        else:
            feedback['summary'] = "Your driving needs significant improvement in multiple areas."
        
        # Identify strengths
        for category in ['acceleration', 'braking', 'cornering', 'phone_usage', 'consistency']:
            if scores.get(category, 0) >= 90:
                if category == 'acceleration':
                    feedback['strengths'].append("Excellent acceleration control - smooth and gradual acceleration patterns.")
                elif category == 'braking':
                    feedback['strengths'].append("Great braking technique - smooth and controlled braking.")
                elif category == 'cornering':
                    feedback['strengths'].append("Excellent cornering - smooth and controlled turns.")
                elif category == 'phone_usage':
                    feedback['strengths'].append("Minimal phone distractions - focused driving.")
                elif category == 'consistency':
                    feedback['strengths'].append("Very consistent driving style - maintaining steady control.")
        
        # Identify areas for improvement
        for category in ['acceleration', 'braking', 'cornering', 'phone_usage', 'consistency']:
            if scores.get(category, 0) < 70:
                if category == 'acceleration':
                    feedback['areas_for_improvement'].append("Work on smoother acceleration - avoid sudden acceleration.")
                    feedback['tips'].append("Gradually press the accelerator instead of pushing it down quickly.")
                elif category == 'braking':
                    feedback['areas_for_improvement'].append("Improve braking technique - avoid harsh braking.")
                    feedback['tips'].append("Anticipate stops earlier and brake gradually.")
                elif category == 'cornering':
                    feedback['areas_for_improvement'].append("Improve cornering technique - take turns more smoothly.")
                    feedback['tips'].append("Slow down before entering turns and accelerate gently when exiting.")
                elif category == 'phone_usage':
                    feedback['areas_for_improvement'].append("Reduce phone distractions while driving.")
                    feedback['tips'].append("Put your phone on 'Do Not Disturb' mode or keep it out of reach while driving.")
                elif category == 'consistency':
                    feedback['areas_for_improvement'].append("Work on maintaining a more consistent driving style.")
                    feedback['tips'].append("Try to maintain steady speed and avoid frequent acceleration and braking.")
        
        # Add event-specific feedback
        if len(events.get('harsh_acceleration', [])) > 0:
            feedback['areas_for_improvement'].append(f"Reduce instances of harsh acceleration (detected {len(events['harsh_acceleration'])} times).")
        
        if len(events.get('harsh_braking', [])) > 0:
            feedback['areas_for_improvement'].append(f"Reduce instances of harsh braking (detected {len(events['harsh_braking'])} times).")
        
        if len(events.get('harsh_cornering', [])) > 0:
            feedback['areas_for_improvement'].append(f"Reduce instances of harsh cornering (detected {len(events['harsh_cornering'])} times).")
        
        if len(events.get('phone_usage', [])) > 0:
            feedback['areas_for_improvement'].append(f"Reduce phone usage while driving (detected {len(events['phone_usage'])} times).")
        
        return feedback
