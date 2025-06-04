from flask import Blueprint, jsonify, current_app  # Import current_app
from entities.models import AreaConfig, ImageTile
from utils.jwt_utils import jwt_required
from services.image_capture_service import ImageCaptureService
from services.image_comparison_service import ImageComparisonService
from extensions import db  # Import db from extensions

monitor_bp = Blueprint('monitor', __name__, url_prefix='/api/monitor')


@monitor_bp.route('/capture/<int:area_config_id>', methods=['POST'])
@jwt_required
def trigger_image_capture(area_config_id):
    config = db.session.query(AreaConfig).get(area_config_id)  # Use db.session.query
    if not config:
        return jsonify({'message': 'AreaConfig not found'}), 404

    # Pass current_app.config to the service method
    ImageCaptureService.capture_images_for_area(config, current_app.config)
    return jsonify({'message': f'Image capture triggered for AreaConfig ID: {area_config_id}'}), 200


@monitor_bp.route('/compare/<int:area_config_id>', methods=['POST'])
@jwt_required
def trigger_image_comparison(area_config_id):
    config = db.session.query(AreaConfig).get(area_config_id)  # Use db.session.query
    if not config:
        return jsonify({'message': 'AreaConfig not found'}), 404

    # Pass current_app.config to the service method
    ImageComparisonService.run_comparison_for_area(config.id, current_app.config)
    return jsonify({'message': f'Image comparison triggered for AreaConfig ID: {area_config_id}'}), 200


@monitor_bp.route('/image-tiles/area/<int:area_config_id>', methods=['GET'])
@jwt_required
def get_area_image_tiles(area_config_id):
    tiles = db.session.query(ImageTile).filter_by(area_config_id=area_config_id).order_by(
        ImageTile.capture_time.desc()).all()
    return jsonify([tile.to_dict() for tile in tiles]), 200
