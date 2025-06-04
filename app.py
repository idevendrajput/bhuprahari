import os
from flask import Flask, jsonify
from flask_cors import CORS

from config import CONFIG_SETTINGS  # Import the dictionary directly
from extensions import db, bcrypt  # Import db and bcrypt from extensions
from mschedule import start_my_schedule  # Import ONLY the scheduler start function

# Import blueprints for routes
from routes.auth_routes import auth_bp
from routes.area_config_routes import area_config_bp
from routes.monitor_routes import monitor_bp
from routes.alert_routes import alert_bp  # NEW: Import the alerts blueprint

# Import FirebaseService to initialize it at app startup
from services.firebase_service import FirebaseService

# --- App Initialization ---
app = Flask(__name__)
app.config.update(CONFIG_SETTINGS)  # Load config from the dictionary
CORS(app)  # Enable CORS for all routes

# Create image storage directory if it doesn't exist
os.makedirs(app.config['IMAGE_STORAGE_DIRECTORY'], exist_ok=True)

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(area_config_bp)
app.register_blueprint(monitor_bp)
app.register_blueprint(alert_bp)  # NEW: Register the alerts blueprint


# --- Health Check ---
@app.route('/', methods=['GET'])
def health_check():
    return jsonify({"message": "Bhuprahari Backend is running!"}), 200


# --- Main execution ---
if __name__ == '__main__':
    # Initialize extensions with the app instance within the main execution block
    # This ensures they are bound to the app before db.create_all() is called.
    db.init_app(app)
    bcrypt.init_app(app)

    with app.app_context():
        db.create_all()  # Create database tables if they don't exist
        print("Database tables created/checked.")

        # Initialize Firebase Admin SDK after app context is available
        FirebaseService.initialize_firebase()

    # Start the scheduler after app context is available
    start_my_schedule(app)  # Pass the app instance here

    app.run(host="0.0.0.0", port=app.config['SERVER_PORT'], debug=True)
