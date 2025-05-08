from flask import jsonify, request, Blueprint
import pandas as pd
import numpy as np
import uuid
import json
import time
from typing import Dict, List, Any, Optional

from app.model.data_processor import DataProcessor
from app.model.scoring_system import ScoringSystem
from app.model.ml_model import DriverBehaviorModel

# In-memory storage for trips
trips = {}
active_trips = {}

trip_controller = Blueprint('trip_controller', __name__)

# Initialize models
data_processor = DataProcessor()
scoring_system = ScoringSystem()
ml_model = DriverBehaviorModel()

# Try to load the model if it exists
ml_model.load()

@trip_controller.route('/trips', methods=['POST'])
def start_trip():
    """Start a new trip and return trip ID."""
    try:
        data = request.json
        
        # Generate a unique trip ID
        trip_id = str(uuid.uuid4())
        
        # Create a new trip record
        trip = {
            'id': trip_id,
            'start_time': int(time.time() * 1000),
            'end_time': None,
            'start_location': data.get('start_location', {}),
            'end_location': None,
            'status': 'active',
            'data': [],
            'events': {
                'harsh_acceleration': [],
                'harsh_braking': [],
                'harsh_cornering': [],
                'phone_usage': [],
                'speeding': []
            },
            'scores': None,
            'feedback': None
        }
        
        # Store the trip
        active_trips[trip_id] = trip
        
        return jsonify({
            'status': 'success',
            'message': 'Trip started successfully',
            'trip_id': trip_id
        }), 201
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@trip_controller.route('/trips/<trip_id>', methods=['PUT'])
def end_trip(trip_id):
    """End a trip and calculate final scores."""
    try:
        if trip_id not in active_trips:
            return jsonify({
                'status': 'error',
                'message': 'Trip not found'
            }), 404
        
        data = request.json
        
        # Update trip with end information
        active_trips[trip_id]['end_time'] = int(time.time() * 1000)
        active_trips[trip_id]['end_location'] = data.get('end_location', {})
        active_trips[trip_id]['status'] = 'completed'
        
        # Process all trip data
        if active_trips[trip_id]['data']:
            trip_data = pd.DataFrame(active_trips[trip_id]['data'])
            
            # Process the trip data
            analysis = data_processor.process_trip_data(trip_data)
            
            # Update trip with analysis results
            active_trips[trip_id]['scores'] = analysis['scores']
            active_trips[trip_id]['events'] = analysis['events']
            
            # Generate feedback
            active_trips[trip_id]['feedback'] = scoring_system.generate_feedback(
                analysis['scores'], 
                analysis['events']
            )
        
        # Move from active to completed trips
        trips[trip_id] = active_trips[trip_id]
        del active_trips[trip_id]
        
        return jsonify({
            'status': 'success',
            'message': 'Trip ended successfully',
            'trip': trips[trip_id]
        }), 200
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@trip_controller.route('/trips/<trip_id>/data', methods=['POST'])
def add_trip_data(trip_id):
    """Add motion data to an active trip."""
    try:
        if trip_id not in active_trips:
            return jsonify({
                'status': 'error',
                'message': 'Trip not found or already completed'
            }), 404
        
        data = request.json
        
        # Validate data format
        required_fields = ['AccX', 'AccY', 'AccZ', 'GyroX', 'GyroY', 'GyroZ', 'Timestamp']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'status': 'error',
                    'message': f'Missing required field: {field}'
                }), 400
        
        # Add data to trip
        active_trips[trip_id]['data'].append(data)
        
        # Process the latest data chunk for real-time feedback
        # Use the last 100 data points or all if less than 100
        data_chunk = active_trips[trip_id]['data'][-100:]
        data_df = pd.DataFrame(data_chunk)
        
        # Get real-time analysis
        realtime_analysis = data_processor.process_realtime_data(data_df)
        
        return jsonify({
            'status': 'success',
            'message': 'Data added successfully',
            'realtime_feedback': realtime_analysis
        }), 200
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@trip_controller.route('/trips/<trip_id>/data/batch', methods=['POST'])
def add_trip_data_batch(trip_id):
    """Add a batch of motion data to an active trip."""
    try:
        if trip_id not in active_trips:
            return jsonify({
                'status': 'error',
                'message': 'Trip not found or already completed'
            }), 404
        
        data_batch = request.json
        
        if not isinstance(data_batch, list):
            return jsonify({
                'status': 'error',
                'message': 'Expected a list of data points'
            }), 400
        
        # Validate data format for each point
        required_fields = ['AccX', 'AccY', 'AccZ', 'GyroX', 'GyroY', 'GyroZ', 'Timestamp']
        for data_point in data_batch:
            for field in required_fields:
                if field not in data_point:
                    return jsonify({
                        'status': 'error',
                        'message': f'Missing required field: {field} in data point'
                    }), 400
        
        # Add data to trip
        active_trips[trip_id]['data'].extend(data_batch)
        
        # Process the latest data chunk for real-time feedback
        # Use the last 100 data points or all if less than 100
        data_chunk = active_trips[trip_id]['data'][-100:]
        data_df = pd.DataFrame(data_chunk)
        
        # Get real-time analysis
        realtime_analysis = data_processor.process_realtime_data(data_df)
        
        return jsonify({
            'status': 'success',
            'message': f'Added {len(data_batch)} data points successfully',
            'realtime_feedback': realtime_analysis
        }), 200
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@trip_controller.route('/trips/<trip_id>', methods=['GET'])
def get_trip(trip_id):
    """Get trip details by ID."""
    try:
        # Check active trips first
        if trip_id in active_trips:
            return jsonify({
                'status': 'success',
                'trip': active_trips[trip_id]
            }), 200
        
        # Then check completed trips
        if trip_id in trips:
            return jsonify({
                'status': 'success',
                'trip': trips[trip_id]
            }), 200
        
        return jsonify({
            'status': 'error',
            'message': 'Trip not found'
        }), 404
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@trip_controller.route('/trips', methods=['GET'])
def get_all_trips():
    """Get all trips."""
    try:
        all_trips = {**trips, **active_trips}
        
        # Convert to list and sort by start time (newest first)
        trip_list = list(all_trips.values())
        trip_list.sort(key=lambda x: x['start_time'], reverse=True)
        
        return jsonify({
            'status': 'success',
            'trips': trip_list
        }), 200
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@trip_controller.route('/trips/<trip_id>/scores', methods=['GET'])
def get_trip_scores(trip_id):
    """Get scores for a specific trip."""
    try:
        # Check active trips first
        if trip_id in active_trips:
            if active_trips[trip_id]['scores'] is None:
                # Calculate preliminary scores based on current data
                if active_trips[trip_id]['data']:
                    trip_data = pd.DataFrame(active_trips[trip_id]['data'])
                    analysis = data_processor.process_trip_data(trip_data)
                    return jsonify({
                        'status': 'success',
                        'trip_id': trip_id,
                        'scores': analysis['scores'],
                        'is_final': False
                    }), 200
                else:
                    return jsonify({
                        'status': 'error',
                        'message': 'No data available for this trip yet'
                    }), 400
            else:
                return jsonify({
                    'status': 'success',
                    'trip_id': trip_id,
                    'scores': active_trips[trip_id]['scores'],
                    'is_final': False
                }), 200
        
        # Then check completed trips
        if trip_id in trips:
            return jsonify({
                'status': 'success',
                'trip_id': trip_id,
                'scores': trips[trip_id]['scores'],
                'is_final': True
            }), 200
        
        return jsonify({
            'status': 'error',
            'message': 'Trip not found'
        }), 404
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@trip_controller.route('/model/train', methods=['POST'])
def train_model():
    """Train the ML model using the provided training data."""
    try:
        # Check if training data path is provided
        data = request.json
        train_data_path = data.get('train_data_path')
        
        if not train_data_path:
            return jsonify({
                'status': 'error',
                'message': 'Training data path is required'
            }), 400
        
        # Train the model
        result = ml_model.train(train_data_path)
        
        if 'error' in result:
            return jsonify({
                'status': 'error',
                'message': result['error']
            }), 500
        
        return jsonify({
            'status': 'success',
            'message': 'Model trained successfully',
            'result': result
        }), 200
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@trip_controller.route('/model/evaluate', methods=['POST'])
def evaluate_model():
    """Evaluate the ML model using the provided test data."""
    try:
        # Check if test data path is provided
        data = request.json
        test_data_path = data.get('test_data_path')
        
        if not test_data_path:
            return jsonify({
                'status': 'error',
                'message': 'Test data path is required'
            }), 400
        
        # Evaluate the model
        result = ml_model.evaluate(test_data_path)
        
        if 'error' in result:
            return jsonify({
                'status': 'error',
                'message': result['error']
            }), 500
        
        return jsonify({
            'status': 'success',
            'message': 'Model evaluated successfully',
            'result': result
        }), 200
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
