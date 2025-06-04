from datetime import datetime, timedelta
import jwt
from functools import wraps
from flask import request, jsonify, current_app  # Keep current_app for request context

# Import User model from entities
from entities.models import User


# Pass app_config to this function
def generate_jwt_token(user_id, token_type='access', app_config=None):
    if app_config is None:
        # Fallback to current_app.config if not explicitly passed (e.g., in request context)
        app_config = current_app.config

    if token_type == 'access':
        expires_delta = timedelta(days=app_config['JWT_ACCESS_TOKEN_EXPIRES_DAYS'])
    elif token_type == 'refresh':
        expires_delta = timedelta(days=app_config['JWT_REFRESH_TOKEN_EXPIRES_DAYS'])
    else:
        raise ValueError("Invalid token_type")

    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + expires_delta,
        'iat': datetime.utcnow(),
        'type': token_type
    }
    return jwt.encode(payload, app_config['JWT_SECRET_KEY'], algorithm='HS256')


# Pass app_config to this function
def decode_jwt_token(token, app_config=None):
    if app_config is None:
        # Fallback to current_app.config if not explicitly passed
        app_config = current_app.config

    try:
        payload = jwt.decode(token, app_config['JWT_SECRET_KEY'], algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return {'error': 'Token has expired'}
    except jwt.InvalidTokenError:
        return {'error': 'Invalid token'}


def jwt_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Ensure db is accessible within the current app context for queries
        from extensions import db  # Local import for db access

        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'message': 'Authorization token is missing!'}), 401

        try:
            token = auth_header.split(" ")[1]  # Expects "Bearer <token>"
            # Pass current_app.config to decode_jwt_token
            payload = decode_jwt_token(token, current_app.config)
            if 'error' in payload:
                return jsonify({'message': payload['error']}), 401

            user_id = payload.get('user_id')
            # Use db.session.query for database operations
            user = db.session.query(User).get(user_id)
            if not user:
                return jsonify({'message': 'User not found!'}), 401

            request.current_user = user  # Attach user object to request
        except IndexError:
            return jsonify({'message': 'Token format is invalid!'}), 401
        except Exception as e:
            return jsonify({'message': f'Something went wrong with token: {str(e)}'}), 401

        return f(*args, **kwargs)

    return decorated_function
