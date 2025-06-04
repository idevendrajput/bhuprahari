 # Define configuration as a dictionary
CONFIG_SETTINGS = {
    'SQLALCHEMY_DATABASE_URI': 'mysql+pymysql://root:Devendra#1123@127.0.0.1:3306/bhuprahari',
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    'Maps_API_KEY': 'AIzaSyAVj_HYKIeMoCtqxDuxZ_eYWzQA5kas8Wc', # Replace with your actual key
    'Maps_STATIC_URL': 'https://maps.googleapis.com/maps/api/staticmap',
    'Maps_IMAGE_SIZE': '400x400', # Image size in pixels (widthxheight)
    'Maps_IMAGE_ZOOM': 21, # Zoom level for 50m x 50m (approx. for Bhilwara latitude)
    'IMAGE_STORAGE_DIRECTORY': './captured_images',
    'JWT_SECRET_KEY': 'your-super-secret-key-that-is-at-least-256-bits-long-and-base64-encoded', # Matches 'jwt.secret'
    'JWT_ACCESS_TOKEN_EXPIRES_DAYS': 1, # Example: 1 day for access token
    'JWT_REFRESH_TOKEN_EXPIRES_DAYS': 30, # Example: 30 days for refresh token
    'SCHEDULING_CRON_EXPRESSION': '0 */5 * * * ?', # Every 5 minutes for testing, '0 0 0 */15 * ?' for 15 days
    'SERVER_PORT': 3300,

    # --- Firebase Configuration ---
    'FIREBASE_SERVICE_ACCOUNT_KEY_PATH': 'path/to/bhuprahari06_firebase_service_account.json', # IMPORTANT: Update this path!
    'FCM_DEFAULT_DEVICE_TOKEN': 'YOUR_FCM_DEVICE_TOKEN_HERE' # For testing, provide a token from a real device
}


#AIzaSyAVj_HYKIeMoCtqxDuxZ_eYWzQA5kas8Wc