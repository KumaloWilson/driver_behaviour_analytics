# Driver Behavior Scoring System

A comprehensive system for analyzing and scoring driver behavior in real-time using motion sensor data.

## Features

- Real-time driver behavior analysis and scoring
- Trip management (start, end, retrieve)
- Comprehensive scoring across multiple driving aspects
- Actionable feedback for drivers
- Support for both REST API and WebSocket interfaces
- Machine learning model for behavior classification

## System Requirements

- Python 3.10 or 3.11 recommended (Python 3.12+ may require additional steps)
- pip package manager
- Virtual environment (recommended)

## Installation Guide

### Step 1: Set Up Your Environment

\`\`\`bash
# Create a new directory for the project
mkdir driver-scoring-system
cd driver-scoring-system

# Clone the repository (if applicable)
# git clone <repository-url>

# Create a virtual environment (recommended)
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
\`\`\`

### Step 2: Install Dependencies

\`\`\`bash
# Install dependencies
pip install -r requirements.txt

# If using Python 3.12+, you may need to install setuptools explicitly
pip install setuptools
\`\`\`

### Step 3: Prepare Your Data

Place your datasets in a data directory:

\`\`\`bash
# Create a data directory
mkdir -p data

# Move your CSV files to this directory
# Example:
# cp /path/to/train_motion_data.csv data/
# cp /path/to/test_motion_data.csv data/
\`\`\`

The system expects CSV files with the following columns:
- AccX, AccY, AccZ: Accelerometer readings
- GyroX, GyroY, GyroZ: Gyroscope readings
- Class: Behavior label (for training data)
- Timestamp: Time information

### Step 4: Train the Model

#### Option 1: Using the built-in training module

\`\`\`bash
python -m app.model.train_model --train data/train_motion_data.csv --test data/test_motion_data.csv
\`\`\`

#### Option 2: Using the standalone training script (for Python 3.12+)

If you encounter dependency issues with Python 3.12+, use the standalone script:

\`\`\`bash
python train_model_standalone.py --train data/train_motion_data.csv --test data/test_motion_data.csv
\`\`\`

This will:
- Process the training data
- Extract features
- Train a Random Forest classifier
- Evaluate the model on the test data
- Save the trained model to `app/model/trained_models/driver_model.pkl`

### Step 5: Run the Server

\`\`\`bash
# Start the Flask server
python run.py
\`\`\`

The server will start on port 5000 by default. You can change this by setting the `PORT` environment variable.

### Step 6: Test the System

You can test the system using the data simulator:

\`\`\`bash
# Run the data simulator with your test data
python -m app.utils.data_simulator --api http://localhost:5000 --csv data/test_motion_data.csv
\`\`\`

For WebSocket testing:

\`\`\`bash
python -m app.utils.data_simulator --api http://localhost:5000 --websocket --csv data/test_motion_data.csv
\`\`\`

## API Usage

### REST API Endpoints

#### Trip Management

- `POST /api/trips` - Start a new trip
- `PUT /api/trips/{trip_id}` - End a trip
- `GET /api/trips/{trip_id}` - Get trip details
- `GET /api/trips` - Get all trips
- `GET /api/trips/{trip_id}/scores` - Get trip scores

#### Data Submission

- `POST /api/trips/{trip_id}/data` - Add a single data point
- `POST /api/trips/{trip_id}/data/batch` - Add multiple data points

#### Model Management

- `POST /api/model/train` - Train the ML model
- `POST /api/model/evaluate` - Evaluate the ML model

### WebSocket Interface

The system provides a WebSocket interface for real-time data streaming:

- Connect to the WebSocket server
- Join a trip room: `join_trip` event with `{trip_id: "..."}`
- Send data: `send_data` event with motion data
- Send batch data: `send_data_batch` event with an array of motion data
- Receive real-time feedback: `realtime_feedback` event

See the API documentation at `/api/docs` for more details.

## Troubleshooting

### Python 3.12+ Compatibility Issues

If you're using Python 3.12 or newer, you might encounter these issues:

1. **Missing distutils module**:
   \`\`\`
   ModuleNotFoundError: No module named 'distutils'
   \`\`\`
   Solution: Install setuptools explicitly
   \`\`\`bash
   pip install setuptools
   \`\`\`

2. **Flask/Werkzeug compatibility issues**:
   \`\`\`
   ImportError: cannot import name 'url_quote' from 'werkzeug.urls'
   \`\`\`
   Solution: Pin Flask and Werkzeug versions
   \`\`\`bash
   pip install flask==2.0.1 werkzeug==2.0.1
   \`\`\`

3. **If issues persist**, use the standalone training script:
   \`\`\`bash
   python train_model_standalone.py --train data/train_motion_data.csv --test data/test_motion_data.csv
   \`\`\`

### Other Common Issues

1. **WebSocket connection issues**:
   - Make sure you have eventlet or gevent installed
   - Try using the REST API if WebSockets aren't working

2. **Data format issues**:
   - Ensure your CSV data matches the expected format
   - Check for missing values or incorrect data types

## License

MIT
