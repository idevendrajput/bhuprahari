# Endpoint to get image tiles for a specific area (for ViewChangesPage)
from flask import jsonify, current_app

from entities.models import ImageTile
from utils.jwt_utils import jwt_required

@current_app.route('/api/image-tiles/area/<int:area_config_id>', methods=['GET'])
@jwt_required  # Protect this route
def get_area_image_tiles(area_config_id):
    # This will return ALL image tiles for the area.
    # The frontend or a separate query might filter for just changed ones or latest.
    tiles = ImageTile.query.filter_by(area_config_id=area_config_id).order_by(ImageTile.capture_time.desc()).all()
    return jsonify([tile.to_dict() for tile in tiles]), 200
