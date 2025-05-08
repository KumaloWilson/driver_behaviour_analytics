from flask import Blueprint, jsonify, render_template, current_app, send_from_directory
import os

# Create a blueprint for API routes
api_routes = Blueprint('api_routes', __name__)

@api_routes.route('/', methods=['GET'])
def index():
    """API root endpoint."""
    return jsonify({
        'name': 'Driver Behavior Scoring API',
        'version': '1.0.0',
        'description': 'API for analyzing and scoring driver behavior',
        'endpoints': {
            'trips': '/api/trips',
            'model': '/api/model',
            'docs': '/api/docs'
        }
    })

@api_routes.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'message': 'Service is running'
    })

@api_routes.route('/docs', methods=['GET'])
def api_docs():
    """API documentation endpoint."""
    try:
        # Try to render the template
        return render_template('api_docs.html')
    except Exception as e:
        # If template rendering fails, serve the comprehensive documentation directly
        current_app.logger.error(f"Error rendering template: {e}")
        return comprehensive_api_docs()

def comprehensive_api_docs():
    """Return comprehensive API documentation as HTML."""
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Driver Behavior Scoring API Documentation</title>
    <style>
        :root {
            --primary-color: #3b82f6;
            --primary-dark: #2563eb;
            --secondary-color: #10b981;
            --text-color: #1f2937;
            --text-light: #6b7280;
            --bg-color: #ffffff;
            --bg-light: #f9fafb;
            --bg-dark: #f3f4f6;
            --border-color: #e5e7eb;
            --code-bg: #f1f5f9;
            --success-color: #10b981;
            --warning-color: #f59e0b;
            --error-color: #ef4444;
            --radius: 6px;
            --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif;
            line-height: 1.6;
            color: var(--text-color);
            background-color: var(--bg-color);
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }

        header {
            background-color: var(--bg-light);
            border-bottom: 1px solid var(--border-color);
            padding: 20px 0;
            margin-bottom: 20px;
            position: sticky;
            top: 0;
            z-index: 100;
        }

        .header-content {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .logo {
            font-size: 24px;
            font-weight: 700;
            color: var(--primary-color);
        }

        .version {
            background-color: var(--primary-color);
            color: white;
            padding: 4px 8px;
            border-radius: var(--radius);
            font-size: 14px;
            font-weight: 500;
        }

        .layout {
            display: flex;
            gap: 30px;
        }

        .sidebar {
            width: 250px;
            position: sticky;
            top: 80px;
            height: calc(100vh - 80px);
            overflow-y: auto;
            padding-right: 15px;
            padding-bottom: 40px;
        }

        .main-content {
            flex: 1;
            max-width: calc(100% - 280px);
            padding-bottom: 60px;
        }

        nav ul {
            list-style: none;
        }

        nav ul li {
            margin-bottom: 5px;
        }

        nav ul li a {
            display: block;
            padding: 8px 12px;
            color: var(--text-color);
            text-decoration: none;
            border-radius: var(--radius);
            font-weight: 500;
            transition: background-color 0.2s;
        }

        nav ul li a:hover {
            background-color: var(--bg-dark);
        }

        nav ul li a.active {
            background-color: var(--primary-color);
            color: white;
        }

        nav .section-title {
            font-size: 14px;
            font-weight: 600;
            text-transform: uppercase;
            color: var(--text-light);
            margin: 20px 0 10px;
            padding-left: 12px;
        }

        h1, h2, h3, h4, h5, h6 {
            margin-bottom: 16px;
            font-weight: 600;
        }

        h1 {
            font-size: 32px;
            margin-bottom: 24px;
        }

        h2 {
            font-size: 24px;
            padding-bottom: 8px;
            border-bottom: 1px solid var(--border-color);
            margin-top: 40px;
        }

        h3 {
            font-size: 20px;
            margin-top: 32px;
        }

        h4 {
            font-size: 18px;
            margin-top: 24px;
        }

        p {
            margin-bottom: 16px;
        }

        a {
            color: var(--primary-color);
            text-decoration: none;
        }

        a:hover {
            text-decoration: underline;
        }

        code {
            font-family: "Fira Code", "Courier New", Courier, monospace;
            background-color: var(--code-bg);
            padding: 2px 4px;
            border-radius: 4px;
            font-size: 14px;
        }

        pre {
            background-color: var(--code-bg);
            padding: 16px;
            border-radius: var(--radius);
            overflow-x: auto;
            margin-bottom: 24px;
        }

        pre code {
            background-color: transparent;
            padding: 0;
            border-radius: 0;
            font-size: 14px;
        }

        .endpoint {
            margin-bottom: 32px;
            border: 1px solid var(--border-color);
            border-radius: var(--radius);
            overflow: hidden;
        }

        .endpoint-header {
            display: flex;
            align-items: center;
            padding: 12px 16px;
            background-color: var(--bg-light);
            border-bottom: 1px solid var(--border-color);
        }

        .http-method {
            font-weight: 600;
            padding: 4px 8px;
            border-radius: 4px;
            margin-right: 12px;
            font-size: 14px;
            min-width: 60px;
            text-align: center;
        }

        .get {
            background-color: #93c5fd;
            color: #1e40af;
        }

        .post {
            background-color: #a7f3d0;
            color: #065f46;
        }

        .put {
            background-color: #fcd34d;
            color: #92400e;
        }

        .delete {
            background-color: #fca5a5;
            color: #b91c1c;
        }

        .endpoint-path {
            font-family: monospace;
            font-weight: 500;
        }

        .endpoint-body {
            padding: 16px;
        }

        .endpoint-description {
            margin-bottom: 16px;
        }

        .params-table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 24px;
        }

        .params-table th,
        .params-table td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid var(--border-color);
        }

        .params-table th {
            background-color: var(--bg-light);
            font-weight: 600;
        }

        .param-name {
            font-family: monospace;
            font-weight: 500;
        }

        .param-type {
            color: var(--text-light);
            font-size: 14px;
        }

        .param-required {
            background-color: var(--error-color);
            color: white;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 500;
        }

        .param-optional {
            background-color: var(--text-light);
            color: white;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 500;
        }

        .tabs {
            display: flex;
            border-bottom: 1px solid var(--border-color);
            margin-bottom: 16px;
        }

        .tab {
            padding: 8px 16px;
            cursor: pointer;
            border-bottom: 2px solid transparent;
            font-weight: 500;
        }

        .tab.active {
            border-bottom-color: var(--primary-color);
            color: var(--primary-color);
        }

        .tab-content {
            display: none;
        }

        .tab-content.active {
            display: block;
        }

        .websocket-event {
            margin-bottom: 24px;
            padding: 16px;
            border: 1px solid var(--border-color);
            border-radius: var(--radius);
            background-color: var(--bg-light);
        }

        .event-name {
            font-family: monospace;
            font-weight: 600;
            margin-bottom: 8px;
        }

        .event-direction {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 500;
            margin-bottom: 12px;
        }

        .client-to-server {
            background-color: #dbeafe;
            color: #1e40af;
        }

        .server-to-client {
            background-color: #dcfce7;
            color: #166534;
        }

        .toc {
            background-color: var(--bg-light);
            padding: 16px;
            border-radius: var(--radius);
            margin-bottom: 32px;
        }

        .toc-title {
            font-weight: 600;
            margin-bottom: 12px;
        }

        .toc ul {
            list-style: none;
            padding-left: 16px;
        }

        .toc ul li {
            margin-bottom: 8px;
        }

        .toc ul li a {
            color: var(--text-color);
            text-decoration: none;
        }

        .toc ul li a:hover {
            color: var(--primary-color);
        }

        .section-divider {
            height: 1px;
            background-color: var(--border-color);
            margin: 40px 0;
        }

        .back-to-top {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background-color: var(--primary-color);
            color: white;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            text-decoration: none;
            box-shadow: var(--shadow);
            opacity: 0;
            transition: opacity 0.3s;
        }

        .back-to-top.visible {
            opacity: 1;
        }

        .back-to-top:hover {
            background-color: var(--primary-dark);
        }

        @media (max-width: 768px) {
            .layout {
                flex-direction: column;
            }

            .sidebar {
                width: 100%;
                position: static;
                height: auto;
                margin-bottom: 30px;
            }

            .main-content {
                max-width: 100%;
            }

            .header-content {
                flex-direction: column;
                align-items: flex-start;
            }

            .version {
                margin-top: 8px;
            }

            .endpoint-header {
                flex-direction: column;
                align-items: flex-start;
            }

            .http-method {
                margin-bottom: 8px;
            }
        }
    </style>
</head>
<body>
    <header>
        <div class="container header-content">
            <div class="logo">Driver Behavior Scoring API</div>
            <div class="version">v1.0.0</div>
        </div>
    </header>

    <div class="container layout">
        <aside class="sidebar">
            <nav>
                <div class="section-title">Getting Started</div>
                <ul>
                    <li><a href="#introduction">Introduction</a></li>
                    <li><a href="#authentication">Authentication</a></li>
                    <li><a href="#base-url">Base URL</a></li>
                    <li><a href="#data-format">Data Format</a></li>
                </ul>

                <div class="section-title">Trip Management</div>
                <ul>
                    <li><a href="#start-trip">Start Trip</a></li>
                    <li><a href="#end-trip">End Trip</a></li>
                    <li><a href="#get-trip">Get Trip</a></li>
                    <li><a href="#get-all-trips">Get All Trips</a></li>
                </ul>

                <div class="section-title">Data Submission</div>
                <ul>
                    <li><a href="#add-data-point">Add Data Point</a></li>
                    <li><a href="#add-data-batch">Add Data Batch</a></li>
                </ul>

                <div class="section-title">Scores</div>
                <ul>
                    <li><a href="#get-trip-scores">Get Trip Scores</a></li>
                </ul>

                <div class="section-title">Model Management</div>
                <ul>
                    <li><a href="#train-model">Train Model</a></li>
                    <li><a href="#evaluate-model">Evaluate Model</a></li>
                </ul>

                <div class="section-title">WebSocket Interface</div>
                <ul>
                    <li><a href="#websocket-connection">Connection</a></li>
                    <li><a href="#websocket-events">Events</a></li>
                    <li><a href="#websocket-example">Example Usage</a></li>
                </ul>

                <div class="section-title">Error Handling</div>
                <ul>
                    <li><a href="#error-format">Error Format</a></li>
                    <li><a href="#error-codes">Error Codes</a></li>
                </ul>
            </nav>
        </aside>

        <main class="main-content">
            <section id="introduction">
                <h1>Driver Behavior Scoring API Documentation</h1>
                <p>
                    This API provides endpoints for analyzing and scoring driver behavior based on motion sensor data.
                    It supports both REST API and WebSocket interfaces for real-time data processing and feedback.
                </p>
                <p>
                    The system analyzes accelerometer and gyroscope data to detect driving events such as harsh acceleration,
                    braking, cornering, and phone usage, and provides comprehensive scoring across multiple driving aspects.
                </p>

                <div class="toc">
                    <div class="toc-title">Table of Contents</div>
                    <ul>
                        <li><a href="#introduction">Introduction</a></li>
                        <li><a href="#authentication">Authentication</a></li>
                        <li><a href="#base-url">Base URL</a></li>
                        <li><a href="#data-format">Data Format</a></li>
                        <li>
                            <a href="#trip-management">Trip Management</a>
                            <ul>
                                <li><a href="#start-trip">Start Trip</a></li>
                                <li><a href="#end-trip">End Trip</a></li>
                                <li><a href="#get-trip">Get Trip</a></li>
                                <li><a href="#get-all-trips">Get All Trips</a></li>
                            </ul>
                        </li>
                        <li>
                            <a href="#data-submission">Data Submission</a>
                            <ul>
                                <li><a href="#add-data-point">Add Data Point</a></li>
                                <li><a href="#add-data-batch">Add Data Batch</a></li>
                            </ul>
                        </li>
                        <li>
                            <a href="#scores">Scores</a>
                            <ul>
                                <li><a href="#get-trip-scores">Get Trip Scores</a></li>
                            </ul>
                        </li>
                        <li>
                            <a href="#model-management">Model Management</a>
                            <ul>
                                <li><a href="#train-model">Train Model</a></li>
                                <li><a href="#evaluate-model">Evaluate Model</a></li>
                            </ul>
                        </li>
                        <li>
                            <a href="#websocket-interface">WebSocket Interface</a>
                            <ul>
                                <li><a href="#websocket-connection">Connection</a></li>
                                <li><a href="#websocket-events">Events</a></li>
                                <li><a href="#websocket-example">Example Usage</a></li>
                            </ul>
                        </li>
                        <li>
                            <a href="#error-handling">Error Handling</a>
                            <ul>
                                <li><a href="#error-format">Error Format</a></li>
                                <li><a href="#error-codes">Error Codes</a></li>
                            </ul>
                        </li>
                    </ul>
                </div>
            </section>

            <section id="authentication">
                <h2>Authentication</h2>
                <p>
                    Currently, the API does not require authentication. This is suitable for development and testing,
                    but for production use, you should implement an authentication mechanism.
                </p>
            </section>

            <section id="base-url">
                <h2>Base URL</h2>
                <p>All API endpoints are relative to the base URL:</p>
                <pre><code>http://localhost:5000/api</code></pre>
                <p>For WebSocket connections, use:</p>
                <pre><code>ws://localhost:5000</code></pre>
            </section>

            <section id="data-format">
                <h2>Data Format</h2>
                <p>The API accepts and returns JSON data. All timestamps are in milliseconds since the Unix epoch.</p>
                <p>The motion data format expected by the API is as follows:</p>
                <pre><code>{
  "AccX": -0.4024278,    // X-axis accelerometer reading (g)
  "AccY": 0.40621805,    // Y-axis accelerometer reading (g)
  "AccZ": -0.42300892,   // Z-axis accelerometer reading (g)
  "GyroX": -0.053603426, // X-axis gyroscope reading (rad/s)
  "GyroY": -0.0067195175, // Y-axis gyroscope reading (rad/s)
  "GyroZ": 0.0011453723, // Z-axis gyroscope reading (rad/s)
  "Timestamp": 1620000100000 // Time in milliseconds since epoch
}</code></pre>
            </section>

            <div class="section-divider"></div>

            <section id="trip-management">
                <h2>Trip Management</h2>
                <p>
                    Trips represent a driving session from a starting point to a destination.
                    The API provides endpoints to start, end, and retrieve trips.
                </p>

                <section id="start-trip">
                    <h3>Start Trip</h3>
                    <div class="endpoint">
                        <div class="endpoint-header">
                            <div class="http-method post">POST</div>
                            <div class="endpoint-path">/trips</div>
                        </div>
                        <div class="endpoint-body">
                            <div class="endpoint-description">
                                Start a new trip and get a trip ID for subsequent data submissions.
                            </div>

                            <h4>Request Body</h4>
                            <table class="params-table">
                                <thead>
                                    <tr>
                                        <th>Parameter</th>
                                        <th>Type</th>
                                        <th>Description</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td class="param-name">start_location</td>
                                        <td class="param-type">Object</td>
                                        <td>
                                            <span class="param-optional">Optional</span>
                                            Starting location information (latitude, longitude, name)
                                        </td>
                                    </tr>
                                </tbody>
                            </table>

                            <h4>Example Request</h4>
                            <pre><code>{
  "start_location": {
    "latitude": 37.7749,
    "longitude": -122.4194,
    "name": "San Francisco"
  }
}</code></pre>

                            <h4>Example Response</h4>
                            <pre><code>{
  "status": "success",
  "message": "Trip started successfully",
  "trip_id": "550e8400-e29b-41d4-a716-446655440000"
}</code></pre>

                            <h4>cURL Example</h4>
                            <pre><code>curl -X POST http://localhost:5000/api/trips \
  -H "Content-Type: application/json" \
  -d '{
    "start_location": {
      "latitude": 37.7749,
      "longitude": -122.4194,
      "name": "San Francisco"
    }
  }'</code></pre>
                        </div>
                    </div>
                </section>

                <section id="end-trip">
                    <h3>End Trip</h3>
                    <div class="endpoint">
                        <div class="endpoint-header">
                            <div class="http-method put">PUT</div>
                            <div class="endpoint-path">/trips/{trip_id}</div>
                        </div>
                        <div class="endpoint-body">
                            <div class="endpoint-description">
                                End a trip and calculate final scores.
                            </div>

                            <h4>Path Parameters</h4>
                            <table class="params-table">
                                <thead>
                                    <tr>
                                        <th>Parameter</th>
                                        <th>Type</th>
                                        <th>Description</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td class="param-name">trip_id</td>
                                        <td class="param-type">String</td>
                                        <td>
                                            <span class="param-required">Required</span>
                                            The ID of the trip to end
                                        </td>
                                    </tr>
                                </tbody>
                            </table>

                            <h4>Request Body</h4>
                            <table class="params-table">
                                <thead>
                                    <tr>
                                        <th>Parameter</th>
                                        <th>Type</th>
                                        <th>Description</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td class="param-name">end_location</td>
                                        <td class="param-type">Object</td>
                                        <td>
                                            <span class="param-optional">Optional</span>
                                            Ending location information (latitude, longitude, name)
                                        </td>
                                    </tr>
                                </tbody>
                            </table>

                            <h4>Example Request</h4>
                            <pre><code>{
  "end_location": {
    "latitude": 37.7833,
    "longitude": -122.4167,
    "name": "San Francisco Downtown"
  }
}</code></pre>

                            <h4>Example Response</h4>
                            <pre><code>{
  "status": "success",
  "message": "Trip ended successfully",
  "trip": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "start_time": 1620000000000,
    "end_time": 1620001000000,
    "start_location": {
      "latitude": 37.7749,
      "longitude": -122.4194,
      "name": "San Francisco"
    },
    "end_location": {
      "latitude": 37.7833,
      "longitude": -122.4167,
      "name": "San Francisco Downtown"
    },
    "status": "completed",
    "scores": {
      "overall": 85.5,
      "acceleration": 90.0,
      "braking": 80.0,
      "cornering": 85.0,
      "phone_usage": 95.0,
      "consistency": 78.0
    },
    "events": {
      "harsh_acceleration": [
        {
          "timestamp": 1620000300000,
          "value": 0.6,
          "duration": 50
        }
      ],
      "harsh_braking": [],
      "harsh_cornering": [],
      "phone_usage": [],
      "speeding": []
    },
    "feedback": {
      "summary": "Very good driving. You showed good control with a few areas for improvement.",
      "strengths": [
        "Excellent acceleration control - smooth and gradual acceleration patterns.",
        "Minimal phone distractions - focused driving."
      ],
      "areas_for_improvement": [
        "Reduce instances of harsh acceleration (detected 1 times)."
      ],
      "tips": [
        "Gradually press the accelerator instead of pushing it down quickly."
      ]
    }
  }
}</code></pre>

                            <h4>cURL Example</h4>
                            <pre><code>curl -X PUT http://localhost:5000/api/trips/550e8400-e29b-41d4-a716-446655440000 \
  -H "Content-Type: application/json" \
  -d '{
    "end_location": {
      "latitude": 37.7833,
      "longitude": -122.4167,
      "name": "San Francisco Downtown"
    }
  }'</code></pre>
                        </div>
                    </div>
                </section>

                <section id="get-trip">
                    <h3>Get Trip</h3>
                    <div class="endpoint">
                        <div class="endpoint-header">
                            <div class="http-method get">GET</div>
                            <div class="endpoint-path">/trips/{trip_id}</div>
                        </div>
                        <div class="endpoint-body">
                            <div class="endpoint-description">
                                Get details for a specific trip.
                            </div>

                            <h4>Path Parameters</h4>
                            <table class="params-table">
                                <thead>
                                    <tr>
                                        <th>Parameter</th>
                                        <th>Type</th>
                                        <th>Description</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td class="param-name">trip_id</td>
                                        <td class="param-type">String</td>
                                        <td>
                                            <span class="param-required">Required</span>
                                            The ID of the trip to retrieve
                                        </td>
                                    </tr>
                                </tbody>
                            </table>

                            <h4>Example Response</h4>
                            <pre><code>{
  "status": "success",
  "trip": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "start_time": 1620000000000,
    "end_time": 1620001000000,
    "start_location": {
      "latitude": 37.7749,
      "longitude": -122.4194,
      "name": "San Francisco"
    },
    "end_location": {
      "latitude": 37.7833,
      "longitude": -122.4167,
      "name": "San Francisco Downtown"
    },
    "status": "completed",
    "scores": {
      "overall": 85.5,
      "acceleration": 90.0,
      "braking": 80.0,
      "cornering": 85.0,
      "phone_usage": 95.0,
      "consistency": 78.0
    }
  }
}</code></pre>

                            <h4>cURL Example</h4>
                            <pre><code>curl -X GET http://localhost:5000/api/trips/550e8400-e29b-41d4-a716-446655440000</code></pre>
                        </div>
                    </div>
                </section>

                <section id="get-all-trips">
                    <h3>Get All Trips</h3>
                    <div class="endpoint">
                        <div class="endpoint-header">
                            <div class="http-method get">GET</div>
                            <div class="endpoint-path">/trips</div>
                        </div>
                        <div class="endpoint-body">
                            <div class="endpoint-description">
                                Get a list of all trips.
                            </div>

                            <h4>Example Response</h4>
                            <pre><code>{
  "status": "success",
  "trips": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "start_time": 1620000000000,
      "end_time": 1620001000000,
      "status": "completed",
      "scores": {
        "overall": 85.5
      }
    },
    {
      "id": "550e8400-e29b-41d4-a716-446655440001",
      "start_time": 1620002000000,
      "end_time": null,
      "status": "active",
      "scores": null
    }
  ]
}</code></pre>

                            <h4>cURL Example</h4>
                            <pre><code>curl -X GET http://localhost:5000/api/trips</code></pre>
                        </div>
                    </div>
                </section>
            </section>

            <div class="section-divider"></div>

            <section id="data-submission">
                <h2>Data Submission</h2>
                <p>
                    These endpoints allow you to submit motion sensor data for a trip.
                    Data can be submitted as individual points or in batches.
                </p>

                <section id="add-data-point">
                    <h3>Add Data Point</h3>
                    <div class="endpoint">
                        <div class="endpoint-header">
                            <div class="http-method post">POST</div>
                            <div class="endpoint-path">/trips/{trip_id}/data</div>
                        </div>
                        <div class="endpoint-body">
                            <div class="endpoint-description">
                                Add a single data point to an active trip.
                            </div>

                            <h4>Path Parameters</h4>
                            <table class="params-table">
                                <thead>
                                    <tr>
                                        <th>Parameter</th>
                                        <th>Type</th>
                                        <th>Description</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td class="param-name">trip_id</td>
                                        <td class="param-type">String</td>
                                        <td>
                                            <span class="param-required">Required</span>
                                            The ID of the trip to add data to
                                        </td>
                                    </tr>
                                </tbody>
                            </table>

                            <h4>Request Body</h4>
                            <table class="params-table">
                                <thead>
                                    <tr>
                                        <th>Parameter</th>
                                        <th>Type</th>
                                        <th>Description</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td class="param-name">AccX</td>
                                        <td class="param-type">Number</td>
                                        <td>
                                            <span class="param-required">Required</span>
                                            X-axis accelerometer reading
                                        </td>
                                    </tr>
                                    <tr>
                                        <td class="param-name">AccY</td>
                                        <td class="param-type">Number</td>
                                        <td>
                                            <span class="param-required">Required</span>
                                            Y-axis accelerometer reading
                                        </td>
                                    </tr>
                                    <tr>
                                        <td class="param-name">AccZ</td>
                                        <td class="param-type">Number</td>
                                        <td>
                                            <span class="param-required">Required</span>
                                            Z-axis accelerometer reading
                                        </td>
                                    </tr>
                                    <tr>
                                        <td class="param-name">GyroX</td>
                                        <td class="param-type">Number</td>
                                        <td>
                                            <span class="param-required">Required</span>
                                            X-axis gyroscope reading
                                        </td>
                                    </tr>
                                    <tr>
                                        <td class="param-name">GyroY</td>
                                        <td class="param-type">Number</td>
                                        <td>
                                            <span class="param-required">Required</span>
                                            Y-axis gyroscope reading
                                        </td>
                                    </tr>
                                    <tr>
                                        <td class="param-name">GyroZ</td>
                                        <td class="param-type">Number</td>
                                        <td>
                                            <span class="param-required">Required</span>
                                            Z-axis gyroscope reading
                                        </td>
                                    </tr>
                                    <tr>
                                        <td class="param-name">Timestamp</td>
                                        <td class="param-type">Number</td>
                                        <td>
                                            <span class="param-required">Required</span>
                                            Time in milliseconds since epoch
                                        </td>
                                    </tr>
                                </tbody>
                            </table>

                            <h4>Example Request</h4>
                            <pre><code>{
  "AccX": -0.4024278,
  "AccY": 0.40621805,
  "AccZ": -0.42300892,
  "GyroX": -0.053603426,
  "GyroY": -0.0067195175,
  "GyroZ": 0.0011453723,
  "Timestamp": 1620000100000
}</code></pre>

                            <h4>Example Response</h4>
                            <pre><code>{
  "status": "success",
  "message": "Data added successfully",
  "realtime_feedback": {
    "current_scores": {
      "overall": 92.5,
      "acceleration": 95.0,
      "braking": 90.0,
      "cornering": 95.0,
      "phone_usage": 100.0,
      "consistency": 85.0
    },
    "current_events": {
      "harsh_acceleration": [],
      "harsh_braking": [],
      "harsh_cornering": [],
      "phone_usage": [],
      "speeding": []
    },
    "current_behavior": "NORMAL"
  }
}</code></pre>

                            <h4>cURL Example</h4>
                            <pre><code>curl -X POST http://localhost:5000/api/trips/550e8400-e29b-41d4-a716-446655440000/data \
  -H "Content-Type: application/json" \
  -d '{
    "AccX": -0.4024278,
    "AccY": 0.40621805,
    "AccZ": -0.42300892,
    "GyroX": -0.053603426,
    "GyroY": -0.0067195175,
    "GyroZ": 0.0011453723,
    "Timestamp": 1620000100000
  }'</code></pre>
                        </div>
                    </div>
                </section>

                <section id="add-data-batch">
                    <h3>Add Data Batch</h3>
                    <div class="endpoint">
                        <div class="endpoint-header">
                            <div class="http-method post">POST</div>
                            <div class="endpoint-path">/trips/{trip_id}/data/batch</div>
                        </div>
                        <div class="endpoint-body">
                            <div class="endpoint-description">
                                Add multiple data points to an active trip in a single request.
                            </div>

                            <h4>Path Parameters</h4>
                            <table class="params-table">
                                <thead>
                                    <tr>
                                        <th>Parameter</th>
                                        <th>Type</th>
                                        <th>Description</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td class="param-name">trip_id</td>
                                        <td class="param-type">String</td>
                                        <td>
                                            <span class="param-required">Required</span>
                                            The ID of the trip to add data to
                                        </td>
                                    </tr>
                                </tbody>
                            </table>

                            <h4>Request Body</h4>
                            <p>An array of data points, each with the same structure as the single data point request.</p>

                            <h4>Example Request</h4>
                            <pre><code>[
  {
    "AccX": -0.4024278,
    "AccY": 0.40621805,
    "AccZ": -0.42300892,
    "GyroX": -0.053603426,
    "GyroY": -0.0067195175,
    "GyroZ": 0.0011453723,
    "Timestamp": 1620000100000
  },
  {
    "AccX": -0.3924278,
    "AccY": 0.41621805,
    "AccZ": -0.41300892,
    "GyroX": -0.043603426,
    "GyroY": -0.0057195175,
    "GyroZ": 0.0021453723,
    "Timestamp": 1620000100100
  }
]</code></pre>

                            <h4>Example Response</h4>
                            <pre><code>{
  "status": "success",
  "message": "Added 2 data points successfully",
  "realtime_feedback": {
    "current_scores": {
      "overall": 93.0,
      "acceleration": 95.0,
      "braking": 92.0,
      "cornering": 95.0,
      "phone_usage": 100.0,
      "consistency": 85.0
    },
    "current_events": {
      "harsh_acceleration": [],
      "harsh_braking": [],
      "harsh_cornering": [],
      "phone_usage": [],
      "speeding": []
    },
    "current_behavior": "NORMAL"
  }
}</code></pre>

                            <h4>cURL Example</h4>
                            <pre><code>curl -X POST http://localhost:5000/api/trips/550e8400-e29b-41d4-a716-446655440000/data/batch \
  -H "Content-Type: application/json" \
  -d '[
    {
      "AccX": -0.4024278,
      "AccY": 0.40621805,
      "AccZ": -0.42300892,
      "GyroX": -0.053603426,
      "GyroY": -0.0067195175,
      "GyroZ": 0.0011453723,
      "Timestamp": 1620000100000
    },
    {
      "AccX": -0.3924278,
      "AccY": 0.41621805,
      "AccZ": -0.41300892,
      "GyroX": -0.043603426,
      "GyroY": -0.0057195175,
      "GyroZ": 0.0021453723,
      "Timestamp": 1620000100100
    }
  ]'</code></pre>
                        </div>
                    </div>
                </section>
            </section>

            <div class="section-divider"></div>

            <section id="scores">
                <h2>Scores</h2>
                <p>
                    These endpoints provide access to trip scores and analysis.
                </p>

                <section id="get-trip-scores">
                    <h3>Get Trip Scores</h3>
                    <div class="endpoint">
                        <div class="endpoint-header">
                            <div class="http-method get">GET</div>
                            <div class="endpoint-path">/trips/{trip_id}/scores</div>
                        </div>
                        <div class="endpoint-body">
                            <div class="endpoint-description">
                                Get scores for a specific trip.
                            </div>

                            <h4>Path Parameters</h4>
                            <table class="params-table">
                                <thead>
                                    <tr>
                                        <th>Parameter</th>
                                        <th>Type</th>
                                        <th>Description</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td class="param-name">trip_id</td>
                                        <td class="param-type">String</td>
                                        <td>
                                            <span class="param-required">Required</span>
                                            The ID of the trip to get scores for
                                        </td>
                                    </tr>
                                </tbody>
                            </table>

                            <h4>Example Response</h4>
                            <pre><code>{
  "status": "success",
  "trip_id": "550e8400-e29b-41d4-a716-446655440000",
  "scores": {
    "overall": 85.5,
    "acceleration": 90.0,
    "braking": 80.0,
    "cornering": 85.0,
    "phone_usage": 95.0,
    "consistency": 78.0
  },
  "is_final": true
}</code></pre>

                            <h4>cURL Example</h4>
                            <pre><code>curl -X GET http://localhost:5000/api/trips/550e8400-e29b-41d4-a716-446655440000/scores</code></pre>
                        </div>
                    </div>
                </section>
            </section>

            <div class="section-divider"></div>

            <section id="model-management">
                <h2>Model Management</h2>
                <p>
                    These endpoints allow you to train and evaluate the machine learning model.
                </p>

                <section id="train-model">
                    <h3>Train Model</h3>
                    <div class="endpoint">
                        <div class="endpoint-header">
                            <div class="http-method post">POST</div>
                            <div class="endpoint-path">/model/train</div>
                        </div>
                        <div class="endpoint-body">
                            <div class="endpoint-description">
                                Train the ML model using the provided training data.
                            </div>

                            <h4>Request Body</h4>
                            <table class="params-table">
                                <thead>
                                    <tr>
                                        <th>Parameter</th>
                                        <th>Type</th>
                                        <th>Description</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td class="param-name">train_data_path</td>
                                        <td class="param-type">String</td>
                                        <td>
                                            <span class="param-required">Required</span>
                                            Path to the training data CSV file
                                        </td>
                                    </tr>
                                </tbody>
                            </table>

                            <h4>Example Request</h4>
                            <pre><code>{
  "train_data_path": "data/train_motion_data.csv"
}</code></pre>

                            <h4>Example Response</h4>
                            <pre><code>{
  "status": "success",
  "message": "Model trained successfully",
  "result": {
    "accuracy": 0.92,
    "classification_report": {
      "NORMAL": {
        "precision": 0.95,
        "recall": 0.93,
        "f1-score": 0.94,
        "support": 150
      },
      "AGGRESSIVE": {
        "precision": 0.88,
        "recall": 0.90,
        "f1-score": 0.89,
        "support": 100
      },
      "SLOW": {
        "precision": 0.92,
        "recall": 0.94,
        "f1-score": 0.93,
        "support": 80
      }
    },
    "model_path": "app/model/trained_models/driver_model.pkl"
  }
}</code></pre>

                            <h4>cURL Example</h4>
                            <pre><code>curl -X POST http://localhost:5000/api/model/train \
  -H "Content-Type: application/json" \
  -d '{
    "train_data_path": "data/train_motion_data.csv"
  }'</code></pre>
                        </div>
                    </div>
                </section>

                <section id="evaluate-model">
                    <h3>Evaluate Model</h3>
                    <div class="endpoint">
                        <div class="endpoint-header">
                            <div class="http-method post">POST</div>
                            <div class="endpoint-path">/model/evaluate</div>
                        </div>
                        <div class="endpoint-body">
                            <div class="endpoint-description">
                                Evaluate the ML model using the provided test data.
                            </div>

                            <h4>Request Body</h4>
                            <table class="params-table">
                                <thead>
                                    <tr>
                                        <th>Parameter</th>
                                        <th>Type</th>
                                        <th>Description</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td class="param-name">test_data_path</td>
                                        <td class="param-type">String</td>
                                        <td>
                                            <span class="param-required">Required</span>
                                            Path to the test data CSV file
                                        </td>
                                    </tr>
                                </tbody>
                            </table>

                            <h4>Example Request</h4>
                            <pre><code>{
  "test_data_path": "data/test_motion_data.csv"
}</code></pre>

                            <h4>Example Response</h4>
                            <pre><code>{
  "status": "success",
  "message": "Model evaluated successfully",
  "result": {
    "accuracy": 0.90,
    "classification_report": {
      "NORMAL": {
        "precision": 0.93,
        "recall": 0.91,
        "f1-score": 0.92,
        "support": 120
      },
      "AGGRESSIVE": {
        "precision": 0.86,
        "recall": 0.88,
        "f1-score": 0.87,
        "support": 80
      },
      "SLOW": {
        "precision": 0.90,
        "recall": 0.92,
        "f1-score": 0.91,
        "support": 60
      }
    }
  }
}</code></pre>

                            <h4>cURL Example</h4>
                            <pre><code>curl -X POST http://localhost:5000/api/model/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "test_data_path": "data/test_motion_data.csv"
  }'</code></pre>
                        </div>
                    </div>
                </section>
            </section>

            <div class="section-divider"></div>

            <section id="websocket-interface">
                <h2>WebSocket Interface</h2>
                <p>
                    The system provides a WebSocket interface for real-time data streaming and feedback.
                    WebSockets are more efficient for high-frequency data transmission compared to REST API calls.
                </p>

                <section id="websocket-connection">
                    <h3>Connection</h3>
                    <p>Connect to the WebSocket server at:</p>
                    <pre><code>ws://localhost:5000/</code></pre>
                </section>

                <section id="websocket-events">
                    <h3>Events</h3>

                    <div class="websocket-event">
                        <div class="event-name">connect</div>
                        <div class="event-direction client-to-server">Client to Server</div>
                        <p>Establish a connection to the WebSocket server.</p>
                        <h4>Response Events</h4>
                        <pre><code>// Server emits 'connection_status' event
{
  "status": "connected",
  "client_id": "abcd1234"
}</code></pre>
                    </div>

                    <div class="websocket-event">
                        <div class="event-name">join_trip</div>
                        <div class="event-direction client-to-server">Client to Server</div>
                        <p>Join a trip room to send data and receive updates for a specific trip.</p>
                        <h4>Payload</h4>
                        <pre><code>{
  "trip_id": "550e8400-e29b-41d4-a716-446655440000"
}</code></pre>
                        <h4>Response Events</h4>
                        <pre><code>// Server emits 'join_status' event
{
  "status": "joined",
  "trip_id": "550e8400-e29b-41d4-a716-446655440000"
}</code></pre>
                    </div>

                    <div class="websocket-event">
                        <div class="event-name">leave_trip</div>
                        <div class="event-direction client-to-server">Client to Server</div>
                        <p>Leave a trip room.</p>
                        <h4>Payload</h4>
                        <pre><code>{
  "trip_id": "550e8400-e29b-41d4-a716-446655440000"
}</code></pre>
                        <h4>Response Events</h4>
                        <pre><code>// Server emits 'leave_status' event
{
  "status": "left",
  "trip_id": "550e8400-e29b-41d4-a716-446655440000"
}</code></pre>
                    </div>

                    <div class="websocket-event">
                        <div class="event-name">send_data</div>
                        <div class="event-direction client-to-server">Client to Server</div>
                        <p>Send a single data point for real-time processing.</p>
                        <h4>Payload</h4>
                        <pre><code>{
  "AccX": -0.4024278,
  "AccY": 0.40621805,
  "AccZ": -0.42300892,
  "GyroX": -0.053603426,
  "GyroY": -0.0067195175,
  "GyroZ": 0.0011453723,
  "Timestamp": 1620000100000
}</code></pre>
                    </div>

                    <div class="websocket-event">
                        <div class="event-name">send_data_batch</div>
                        <div class="event-direction client-to-server">Client to Server</div>
                        <p>Send multiple data points for real-time processing.</p>
                        <h4>Payload</h4>
                        <pre><code>[
  {
    "AccX": -0.4024278,
    "AccY": 0.40621805,
    "AccZ": -0.42300892,
    "GyroX": -0.053603426,
    "GyroY": -0.0067195175,
    "GyroZ": 0.0011453723,
    "Timestamp": 1620000100000
  },
  {
    "AccX": -0.3924278,
    "AccY": 0.41621805,
    "AccZ": -0.41300892,
    "GyroX": -0.043603426,
    "GyroY": -0.0057195175,
    "GyroZ": 0.0021453723,
    "Timestamp": 1620000100100
  }
]</code></pre>
                    </div>

                    <div class="websocket-event">
                        <div class="event-name">realtime_feedback</div>
                        <div class="event-direction server-to-client">Server to Client</div>
                        <p>Receive real-time feedback based on processed data.</p>
                        <h4>Payload</h4>
                        <pre><code>{
  "trip_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": 1620000100500,
  "analysis": {
    "current_scores": {
      "overall": 92.5,
      "acceleration": 95.0,
      "braking": 90.0,
      "cornering": 95.0,
      "phone_usage": 100.0,
      "consistency": 85.0
    },
    "current_events": {
      "harsh_acceleration": [],
      "harsh_braking": [],
      "harsh_cornering": [],
      "phone_usage": [],
      "speeding": []
    },
    "current_behavior": "NORMAL"
  }
}</code></pre>
                    </div>

                    <div class="websocket-event">
                        <div class="event-name">trip_update</div>
                        <div class="event-direction server-to-client">Server to Client</div>
                        <p>Receive updates about a trip (broadcast to all clients in the trip room).</p>
                        <h4>Payload</h4>
                        <pre><code>{
  "trip_id": "550e8400-e29b-41d4-a716-446655440000",
  "client_id": "abcd1234",
  "timestamp": 1620000100500,
  "analysis": {
    "current_scores": {
      "overall": 92.5,
      "acceleration": 95.0,
      "braking": 90.0,
      "cornering": 95.0,
      "phone_usage": 100.0,
      "consistency": 85.0
    },
    "current_events": {
      "harsh_acceleration": [],
      "harsh_braking": [],
      "harsh_cornering": [],
      "phone_usage": [],
      "speeding": []
    },
    "current_behavior": "NORMAL"
  }
}</code></pre>
                    </div>

                    <div class="websocket-event">
                        <div class="event-name">error</div>
                        <div class="event-direction server-to-client">Server to Client</div>
                        <p>Receive error messages from the server.</p>
                        <h4>Payload</h4>
                        <pre><code>{
  "message": "Error message"
}</code></pre>
                    </div>
                </section>

                <section id="websocket-example">
                    <h3>Example Usage</h3>
                    <p>Here's an example of how to use the WebSocket interface with JavaScript:</p>
                    <pre><code>// Connect to the WebSocket server
const socket = io('http://localhost:5000');

// Handle connection event
socket.on('connect', () => {
  console.log('Connected to server');
});

// Handle connection status event
socket.on('connection_status', (data) => {
  console.log('Connection status:', data);
  
  // Start a trip via REST API
  fetch('http://localhost:5000/api/trips', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      start_location: {
        latitude: 37.7749,
        longitude: -122.4194,
        name: 'San Francisco'
      }
    })
  })
  .then(response => response.json())
  .then(data => {
    const tripId = data.trip_id;
    console.log('Trip started with ID:', tripId);
    
    // Join the trip room
    socket.emit('join_trip', { trip_id: tripId });
  });
});

// Handle join status event
socket.on('join_status', (data) => {
  console.log('Join status:', data);
  
  // Start sending data
  sendMotionData(data.trip_id);
});

// Handle realtime feedback event
socket.on('realtime_feedback', (data) => {
  console.log('Realtime feedback:', data);
});

// Handle error event
socket.on('error', (data) => {
  console.error('Error:', data);
});

// Function to send motion data
function sendMotionData(tripId) {
  // Example data point
  const dataPoint = {
    AccX: -0.4024278,
    AccY: 0.40621805,
    AccZ: -0.42300892,
    GyroX: -0.053603426,
    GyroY: -0.0067195175,
    GyroZ: 0.0011453723,
    Timestamp: Date.now()
  };
  
  // Send data point
  socket.emit('send_data', dataPoint);
  
  // Send data every second
  setTimeout(() => sendMotionData(tripId), 1000);
}</code></pre>
                </section>
            </section>

            <div class="section-divider"></div>

            <section id="error-handling">
                <h2>Error Handling</h2>
                <p>
                    The API uses standard HTTP status codes to indicate the success or failure of requests.
                    In case of an error, the response will include a JSON object with details about the error.
                </p>

                <section id="error-format">
                    <h3>Error Response Format</h3>
                    <pre><code>{
  "status": "error",
  "message": "Error message"
}</code></pre>
                </section>

                <section id="error-codes">
                    <h3>Common Error Codes</h3>
                    <table class="params-table">
                        <thead>
                            <tr>
                                <th>Status Code</th>
                                <th>Description</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>400</td>
                                <td>Bad Request - The request was invalid or cannot be served</td>
                            </tr>
                            <tr>
                                <td>404</td>
                                <td>Not Found - The requested resource does not exist</td>
                            </tr>
                            <tr>
                                <td>500</td>
                                <td>Internal Server Error - An error occurred on the server</td>
                            </tr>
                        </tbody>
                    </table>

                    <h4>Example Error Response</h4>
                    <pre><code>{
  "status": "error",
  "message": "Trip not found"
}</code></pre>
                </section>
            </section>
        </main>
    </div>

    <a href="#" class="back-to-top" id="back-to-top">↑</a>

    <script>
        // Show/hide back to top button
        window.addEventListener('scroll', function() {
            const backToTop = document.getElementById('back-to-top');
            if (window.scrollY > 300) {
                backToTop.classList.add('visible');
            } else {
                backToTop.classList.remove('visible');
            }
        });

        // Smooth scroll to top
        document.getElementById('back-to-top').addEventListener('click', function(e) {
            e.preventDefault();
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });

        // Highlight active section in sidebar
        window.addEventListener('scroll', function() {
            const sections = document.querySelectorAll('section[id]');
            const navLinks = document.querySelectorAll('nav ul li a');
            
            let currentSection = '';
            
            sections.forEach(section => {
                const sectionTop = section.offsetTop - 100;
                const sectionHeight = section.offsetHeight;
                
                if (window.scrollY >= sectionTop && window.scrollY < sectionTop + sectionHeight) {
                    currentSection = section.getAttribute('id');
                }
            });
            
            navLinks.forEach(link => {
                link.classList.remove('active');
                if (link.getAttribute('href') === `#${currentSection}`) {
                    link.classList.add('active');
                }
            });
        });
    </script>
</body>
</html>
    """
