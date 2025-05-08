import pandas as pd
import numpy as np
import time
import requests
import json
import argparse
import socketio
from typing import Dict, List, Any

class DriverDataSimulator:
    def __init__(self, api_url: str, use_websocket: bool = False):
        """Initialize the driver data simulator."""
        self.api_url = api_url
        self.use_websocket = use_websocket
        self.trip_id = None
        self.sio = None
        
        if use_websocket:
            # Initialize Socket.IO client
            self.sio = socketio.Client()
            self.setup_socketio()
    
    def setup_socketio(self):
        """Set up Socket.IO event handlers."""
        @self.sio.event
        def connect():
            print("Connected to WebSocket server")
        
        @self.sio.event
        def disconnect():
            print("Disconnected from WebSocket server")
        
        @self.sio.event
        def connection_status(data):
            print(f"Connection status: {data}")
        
        @self.sio.event
        def join_status(data):
            print(f"Join status: {data}")
        
        @self.sio.event
        def realtime_feedback(data):
            print(f"Received real-time feedback: {json.dumps(data, indent=2)}")
        
        @self.sio.event
        def error(data):
            print(f"Error: {data}")
    
    def connect_websocket(self):
        """Connect to the WebSocket server."""
        if self.use_websocket and self.sio:
            try:
                self.sio.connect(self.api_url)
                return True
            except Exception as e:
                print(f"Error connecting to WebSocket server: {e}")
                return False
        return False
    
    def disconnect_websocket(self):
        """Disconnect from the WebSocket server."""
        if self.use_websocket and self.sio and self.sio.connected:
            self.sio.disconnect()
    
    def start_trip(self, start_location: Dict[str, float] = None) -> str:
        """Start a new trip and return the trip ID."""
        if start_location is None:
            start_location = {
                'latitude': 37.7749,
                'longitude': -122.4194,
                'name': 'San Francisco'
            }
        
        try:
            response = requests.post(
                f"{self.api_url}/api/trips",
                json={'start_location': start_location},
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 201:
                data = response.json()
                self.trip_id = data.get('trip_id')
                
                # Join trip room if using WebSocket
                if self.use_websocket and self.sio and self.sio.connected:
                    self.sio.emit('join_trip', {'trip_id': self.trip_id})
                
                return self.trip_id
            else:
                print(f"Error starting trip: {response.text}")
                return None
        
        except Exception as e:
            print(f"Error starting trip: {e}")
            return None
    
    def end_trip(self, end_location: Dict[str, float] = None) -> bool:
        """End the current trip."""
        if not self.trip_id:
            print("No active trip to end")
            return False
        
        if end_location is None:
            end_location = {
                'latitude': 37.7833,
                'longitude': -122.4167,
                'name': 'San Francisco Downtown'
            }
        
        try:
            response = requests.put(
                f"{self.api_url}/api/trips/{self.trip_id}",
                json={'end_location': end_location},
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Leave trip room if using WebSocket
                if self.use_websocket and self.sio and self.sio.connected:
                    self.sio.emit('leave_trip', {'trip_id': self.trip_id})
                
                # Print trip results
                print("\nTrip Results:")
                print(f"Trip ID: {self.trip_id}")
                print(f"Status: {data['trip']['status']}")
                print("\nScores:")
                for category, score in data['trip']['scores'].items():
                    print(f"  {category.capitalize()}: {score}")
                
                print("\nFeedback:")
                print(f"  Summary: {data['trip']['feedback']['summary']}")
                
                if data['trip']['feedback']['strengths']:
                    print("\n  Strengths:")
                    for strength in data['trip']['feedback']['strengths']:
                        print(f"    - {strength}")
                
                if data['trip']['feedback']['areas_for_improvement']:
                    print("\n  Areas for Improvement:")
                    for area in data['trip']['feedback']['areas_for_improvement']:
                        print(f"    - {area}")
                
                if data['trip']['feedback']['tips']:
                    print("\n  Tips:")
                    for tip in data['trip']['feedback']['tips']:
                        print(f"    - {tip}")
                
                # Reset trip ID
                self.trip_id = None
                
                return True
            else:
                print(f"Error ending trip: {response.text}")
                return False
        
        except Exception as e:
            print(f"Error ending trip: {e}")
            return False
    
    def send_data_point(self, data_point: Dict[str, Any]) -> bool:
        """Send a single data point to the server."""
        if not self.trip_id:
            print("No active trip to send data to")
            return False
        
        try:
            # Add timestamp if not present
            if 'Timestamp' not in data_point:
                data_point['Timestamp'] = int(time.time() * 1000)
            
            if self.use_websocket and self.sio and self.sio.connected:
                # Send via WebSocket
                self.sio.emit('send_data', data_point)
                return True
            else:
                # Send via REST API
                response = requests.post(
                    f"{self.api_url}/api/trips/{self.trip_id}/data",
                    json=data_point,
                    headers={'Content-Type': 'application/json'}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return True
                else:
                    print(f"Error sending data: {response.text}")
                    return False
        
        except Exception as e:
            print(f"Error sending data: {e}")
            return False
    
    def send_data_batch(self, data_batch: List[Dict[str, Any]]) -> bool:
        """Send a batch of data points to the server."""
        if not self.trip_id:
            print("No active trip to send data to")
            return False
        
        try:
            # Add timestamps if not present
            for i, data_point in enumerate(data_batch):
                if 'Timestamp' not in data_point:
                    data_point['Timestamp'] = int(time.time() * 1000) + i
            
            if self.use_websocket and self.sio and self.sio.connected:
                # Send via WebSocket
                self.sio.emit('send_data_batch', data_batch)
                return True
            else:
                # Send via REST API
                response = requests.post(
                    f"{self.api_url}/api/trips/{self.trip_id}/data/batch",
                    json=data_batch,
                    headers={'Content-Type': 'application/json'}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return True
                else:
                    print(f"Error sending data batch: {response.text}")
                    return False
        
        except Exception as e:
            print(f"Error sending data batch: {e}")
            return False
    
    def simulate_trip_from_csv(self, csv_path: str, batch_size: int = 10, delay: float = 0.1) -> bool:
        """Simulate a trip using data from a CSV file."""
        try:
            # Load data
            data = pd.read_csv(csv_path)
            
            # Start trip
            trip_id = self.start_trip()
            if not trip_id:
                return False
            
            print(f"Started trip with ID: {trip_id}")
            print(f"Simulating trip with {len(data)} data points...")
            
            # Send data in batches
            for i in range(0, len(data), batch_size):
                batch = data.iloc[i:i+batch_size].to_dict('records')
                success = self.send_data_batch(batch)
                
                if not success:
                    print(f"Failed to send batch at index {i}")
                    return False
                
                # Sleep to simulate real-time data
                time.sleep(delay)
                
                # Print progress
                if i % 100 == 0:
                    print(f"Sent {i} data points...")
            
            print(f"Sent all {len(data)} data points")
            
            # End trip
            return self.end_trip()
        
        except Exception as e:
            print(f"Error simulating trip: {e}")
            return False

def main():
    """Run the driver data simulator."""
    parser = argparse.ArgumentParser(description='Simulate driver data for testing')
    parser.add_argument('--api', default='http://localhost:5000', help='API URL')
    parser.add_argument('--websocket', action='store_true', help='Use WebSocket instead of REST API')
    parser.add_argument('--csv', required=True, help='Path to CSV file with driver data')
    parser.add_argument('--batch', type=int, default=10, help='Batch size for sending data')
    parser.add_argument('--delay', type=float, default=0.1, help='Delay between batches (seconds)')
    
    args = parser.parse_args()
    
    # Initialize simulator
    simulator = DriverDataSimulator(args.api, args.websocket)
    
    # Connect to WebSocket if needed
    if args.websocket:
        if not simulator.connect_websocket():
            print("Failed to connect to WebSocket server")
            return
    
    # Simulate trip
    success = simulator.simulate_trip_from_csv(args.csv, args.batch, args.delay)
    
    # Disconnect from WebSocket if needed
    if args.websocket:
        simulator.disconnect_websocket()
    
    if success:
        print("Trip simulation completed successfully")
    else:
        print("Trip simulation failed")

if __name__ == '__main__':
    main()
