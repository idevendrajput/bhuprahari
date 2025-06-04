from flask import Blueprint, jsonify
from entities.models import AlertSession, AlertDetail, ImageTile, AreaConfig
from extensions import db  # Import db from extensions
from utils.jwt_utils import jwt_required

alert_bp = Blueprint('alerts', __name__, url_prefix='/api/alerts')


@alert_bp.route('/sessions', methods=['GET'])
@jwt_required
def get_alert_sessions():
    """
    Retrieves a list of all alert sessions.
    """
    sessions = db.session.query(AlertSession).order_by(AlertSession.start_time.desc()).all()
    return jsonify([session.to_dict() for session in sessions]), 200


@alert_bp.route('/sessions/<int:session_id>/details', methods=['GET'])
@jwt_required
def get_alert_session_details(session_id):
    """
    Retrieves details for a specific alert session, including associated image tiles.
    """
    session = db.session.query(AlertSession).get(session_id)
    if not session:
        return jsonify({'message': 'Alert session not found'}), 404

    details = db.session.query(AlertDetail).filter_by(alert_session_id=session_id).all()

    # Optionally, fetch associated image tile info and previous/current image paths
    detailed_alerts = []
    for detail in details:
        current_tile = db.session.query(ImageTile).get(detail.image_tile_id)

        alert_dict = detail.to_dict()
        alert_dict['current_tile_info'] = current_tile.to_dict() if current_tile else None

        # We already store previous_image_path and current_image_path in AlertDetail
        # You might want to ensure these paths are accessible from the frontend if needed
        # (e.g., by serving them as static files or through a dedicated endpoint)

        detailed_alerts.append(alert_dict)

    session_dict = session.to_dict()
    session_dict['alert_details'] = detailed_alerts

    return jsonify(session_dict), 200

