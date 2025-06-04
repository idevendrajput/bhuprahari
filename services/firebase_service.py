import os
import firebase_admin
from firebase_admin import credentials, messaging
from flask import current_app # To access app.config

class FirebaseService:
    _initialized = False

    @classmethod
    def initialize_firebase(cls):
        if not cls._initialized:
            try:
                # Ensure app context is available to access current_app.config
                with current_app.app_context():
                    service_account_key_path = current_app.config.get('FIREBASE_SERVICE_ACCOUNT_KEY_PATH')
                    if not service_account_key_path or not os.path.exists(service_account_key_path):
                        print(f"FIREBASE_SERVICE_ACCOUNT_KEY_PATH not found or invalid: {service_account_key_path}")
                        return False

                    cred = credentials.Certificate(service_account_key_path)
                    firebase_admin.initialize_app(cred)
                    cls._initialized = True
                    print("Firebase Admin SDK initialized successfully.")
                    return True
            except Exception as e:
                print(f"Error initializing Firebase Admin SDK: {e}")
                return False
        return True

    @staticmethod
    def send_notification(title, body, device_token=None, data_payload=None):
        if not FirebaseService._initialized:
            print("Firebase Admin SDK not initialized. Cannot send notification.")
            return False

        if device_token is None:
            # Fallback to a default token if not provided (for testing)
            device_token = current_app.config.get('FCM_DEFAULT_DEVICE_TOKEN')
            if not device_token:
                print("No device token provided and FCM_DEFAULT_DEVICE_TOKEN not set. Cannot send notification.")
                return False

        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            data=data_payload, # Optional data payload
            token=device_token,
        )

        try:
            response = messaging.send(message)
            print(f"Successfully sent Firebase notification: {response}")
            return True
        except Exception as e:
            print(f"Error sending Firebase notification: {e}")
            return False

