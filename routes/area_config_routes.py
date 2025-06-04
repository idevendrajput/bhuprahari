from flask import Blueprint, request, jsonify
from entities.models import AreaConfig
from extensions import db
from utils.jwt_utils import jwt_required

area_config_bp = Blueprint('area_config', __name__, url_prefix='/api/area-configs')

@area_config_bp.route('/', methods=['POST'])
@jwt_required
def create_area_config():
    data = request.get_json()
    try:
        new_config = AreaConfig(
            name=data['name'],
            center_lat=data['centerLat'],
            center_lon=data['centerLon'],
            north_km=data['northKm'],
            south_km=data['southKm'],
            east_km=data['eastKm'],
            west_km=data['westKm']
        )
        db.session.add(new_config)
        db.session.commit()
        return jsonify(new_config.to_dict()), 201
    except KeyError as e:
        return jsonify({'message': f'Missing data for: {e}'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error creating area config: {str(e)}'}), 500

@area_config_bp.route('/', methods=['GET'])
@jwt_required
def get_all_area_configs():
    configs = AreaConfig.query.all()
    return jsonify([config.to_dict() for config in configs]), 200

@area_config_bp.route('/<int:config_id>', methods=['GET'])
@jwt_required
def get_area_config(config_id):
    config = AreaConfig.query.get(config_id)
    if not config:
        return jsonify({'message': 'AreaConfig not found'}), 404
    return jsonify(config.to_dict()), 200
