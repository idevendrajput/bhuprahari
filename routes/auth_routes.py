from flask import Blueprint, request, jsonify, current_app  # Import current_app
from entities.models import User
from utils.jwt_utils import generate_jwt_token
from extensions import db  # Import db and bcrypt from extensions

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    profile = data.get('profile')

    if not email or not password:
        return jsonify({'message': 'Email and password are required'}), 400

    if db.session.query(User).filter_by(email=email).first():  # Use db.session.query
        return jsonify({'message': 'User with this email already exists'}), 409

    new_user = User(email=email, profile=profile)
    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully', 'user': new_user.to_dict()}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = db.session.query(User).filter_by(email=email).first()  # Use db.session.query

    if not user or not user.check_password(password):
        return jsonify({'message': 'Invalid credentials'}), 401

    # Pass current_app.config to generate_jwt_token
    access_token = generate_jwt_token(user.id, 'access', current_app.config)
    refresh_token = generate_jwt_token(user.id, 'refresh', current_app.config)

    return jsonify({
        'message': 'Login successful',
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': user.to_dict()
    }), 200
