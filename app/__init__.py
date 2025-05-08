from flask import Flask, redirect, url_for
from flask_socketio import SocketIO
from flask_cors import CORS
import os

# Initialize SocketIO
socketio = SocketIO()

def create_app(test_config=None):
    """Create and configure the Flask application."""
    app = Flask(__name__, 
                instance_relative_config=True,
                template_folder='view/templates',
                static_folder='view/static')
    
    # Enable CORS
    CORS(app)
    
    # Configure the app
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev'),
        DEBUG=os.environ.get('FLASK_ENV', 'development') == 'development'
    )
    
    if test_config is None:
        # Load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Load the test config if passed in
        app.config.from_mapping(test_config)
    
    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    # Add a root route that redirects to the API docs
    @app.route('/')
    def index():
        return redirect('/api/docs')
    
    # Add a /docs route that redirects to the API docs
    @app.route('/docs')
    def docs():
        return redirect('/api/docs')
    
    # Register blueprints
    from app.view.api_routes import api_routes
    from app.controller.trip_controller import trip_controller
    
    app.register_blueprint(api_routes, url_prefix='/api')
    app.register_blueprint(trip_controller, url_prefix='/api')
    
    # Initialize SocketIO with the app
    socketio.init_app(app, cors_allowed_origins="*")
    
    # Initialize WebSocket controllers
    from app.controller.websocket_controller import init_socketio
    init_socketio(socketio)
    
    return app
