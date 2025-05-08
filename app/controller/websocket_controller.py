from flask_socketio import SocketIO, emit, join_room, leave_room
from flask import request, current_app
import pandas as pd
import json
import time
import threading
from typing import Dict, Any

from app.model.data_processor import DataProcessor

# Initialize data processor
data_processor = DataProcessor()

# In-memory storage for active WebSocket connections
active_connections = {}

def init_socketio(socketio: SocketIO):
    """Initialize WebSocket event handlers."""
    
    @socketio.on('connect')
    def handle_connect():
        """Handle client connection."""
        client_id = request.sid
        active_connections[client_id] = {
            'trip_id': None,
            'last_update': time.time(),
            'data_buffer': []
        }
        emit('connection_status', {'status': 'connected', 'client_id': client_id})
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnection."""
        client_id = request.sid
        if client_id in active_connections:
            # Clean up any trip association
            trip_id = active_connections[client_id]['trip_id']
            if trip_id:
                leave_room(f'trip_{trip_id}')
            
            # Remove client from active connections
            del active_connections[client_id]
    
    @socketio.on('join_trip')
    def handle_join_trip(data):
        """Handle client joining a trip room."""
        client_id = request.sid
        trip_id = data.get('trip_id')
        
        if not trip_id:
            emit('error', {'message': 'Trip ID is required'})
            return
        
        # Update client's trip association
        if client_id in active_connections:
            active_connections[client_id]['trip_id'] = trip_id
            active_connections[client_id]['last_update'] = time.time()
            
            # Join the trip room
            join_room(f'trip_{trip_id}')
            
            emit('join_status', {
                'status': 'joined',
                'trip_id': trip_id
            })
    
    @socketio.on('leave_trip')
    def handle_leave_trip(data):
        """Handle client leaving a trip room."""
        client_id = request.sid
        trip_id = data.get('trip_id')
        
        if not trip_id:
            emit('error', {'message': 'Trip ID is required'})
            return
        
        # Update client's trip association
        if client_id in active_connections and active_connections[client_id]['trip_id'] == trip_id:
            active_connections[client_id]['trip_id'] = None
            
            # Leave the trip room
            leave_room(f'trip_{trip_id}')
            
            emit('leave_status', {
                'status': 'left',
                'trip_id': trip_id
            })
    
    @socketio.on('send_data')
    def handle_send_data(data):
        """Handle real-time data from client."""
        client_id = request.sid
        
        if client_id not in active_connections:
            emit('error', {'message': 'Not connected'})
            return
        
        trip_id = active_connections[client_id]['trip_id']
        
        if not trip_id:
            emit('error', {'message': 'Not associated with a trip'})
            return
        
        # Validate data format
        required_fields = ['AccX', 'AccY', 'AccZ', 'GyroX', 'GyroY', 'GyroZ', 'Timestamp']
        for field in required_fields:
            if field not in data:
                emit('error', {'message': f'Missing required field: {field}'})
                return
        
        # Add data to buffer
        active_connections[client_id]['data_buffer'].append(data)
        active_connections[client_id]['last_update'] = time.time()
        
        # Process data if buffer is large enough
        if len(active_connections[client_id]['data_buffer']) >= 10:
            process_data_buffer(client_id, trip_id, socketio)
    
    @socketio.on('send_data_batch')
    def handle_send_data_batch(data):
        """Handle batch of real-time data from client."""
        client_id = request.sid
        
        if client_id not in active_connections:
            emit('error', {'message': 'Not connected'})
            return
        
        trip_id = active_connections[client_id]['trip_id']
        
        if not trip_id:
            emit('error', {'message': 'Not associated with a trip'})
            return
        
        if not isinstance(data, list):
            emit('error', {'message': 'Expected a list of data points'})
            return
        
        # Validate data format for each point
        required_fields = ['AccX', 'AccY', 'AccZ', 'GyroX', 'GyroY', 'GyroZ', 'Timestamp']
        for data_point in data:
            for field in required_fields:
                if field not in data_point:
                    emit('error', {'message': f'Missing required field: {field} in data point'})
                    return
        
        # Add data to buffer
        active_connections[client_id]['data_buffer'].extend(data)
        active_connections[client_id]['last_update'] = time.time()
        
        # Process data
        process_data_buffer(client_id, trip_id, socketio)
    
    # Start the background task for processing pending data
    start_background_task(socketio)

def process_data_buffer(client_id: str, trip_id: str, socketio: SocketIO):
    """Process the data buffer for a client and emit results."""
    if client_id not in active_connections:
        return
    
    # Get data buffer
    data_buffer = active_connections[client_id]['data_buffer']
    
    if not data_buffer:
        return
    
    # Convert to DataFrame
    data_df = pd.DataFrame(data_buffer)
    
    # Process data
    analysis = data_processor.process_realtime_data(data_df)
    
    # Emit results to the client
    socketio.emit('realtime_feedback', {
        'trip_id': trip_id,
        'timestamp': int(time.time() * 1000),
        'analysis': analysis
    }, room=client_id)
    
    # Also emit to the trip room for any observers
    socketio.emit('trip_update', {
        'trip_id': trip_id,
        'client_id': client_id,
        'timestamp': int(time.time() * 1000),
        'analysis': analysis
    }, room=f'trip_{trip_id}')
    
    # Clear the buffer
    active_connections[client_id]['data_buffer'] = []

def process_pending_data(socketio: SocketIO):
    """Process any pending data in client buffers."""
    current_time = time.time()
    
    for client_id, client_data in list(active_connections.items()):
        # If there's data in the buffer and it's been more than 1 second since the last update
        if (client_data['data_buffer'] and 
            current_time - client_data['last_update'] > 1 and 
            client_data['trip_id']):
            
            process_data_buffer(client_id, client_data['trip_id'], socketio)

def background_task(socketio: SocketIO):
    """Background task to periodically process pending data."""
    while True:
        process_pending_data(socketio)
        time.sleep(1)  # Sleep for 1 second

def start_background_task(socketio: SocketIO):
    """Start the background task in a separate thread."""
    thread = threading.Thread(target=background_task, args=(socketio,))
    thread.daemon = True  # Daemon threads are killed when the main program exits
    thread.start()
