from datetime import datetime
from extensions import db, bcrypt # Import db and bcrypt from extensions

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    profile = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_update = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'profile': self.profile,
            'createdAt': self.created_at.isoformat(),
            'lastUpdate': self.last_update.isoformat()
        }

class AreaConfig(db.Model):
    __tablename__ = 'area_configs'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    center_lat = db.Column(db.Float, nullable=False)
    center_lon = db.Column(db.Float, nullable=False)
    north_km = db.Column(db.Float, nullable=False)
    south_km = db.Column(db.Float, nullable=False)
    east_km = db.Column(db.Float, nullable=False)
    west_km = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'centerLat': self.center_lat,
            'centerLon': self.center_lon,
            'northKm': self.north_km,
            'southKm': self.south_km,
            'eastKm': self.east_km,
            'westKm': self.west_km,
            'createdAt': self.created_at.isoformat()
        }

class ImageTile(db.Model):
    __tablename__ = 'image_tiles'
    id = db.Column(db.Integer, primary_key=True)
    area_config_id = db.Column(db.Integer, db.ForeignKey('area_configs.id'), nullable=False)
    unique_key = db.Column(db.String(255), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    capture_time = db.Column(db.DateTime, nullable=False)
    image_path = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(50), nullable=False) # e.g., 'INITIAL', 'CAPTURED', 'COMPARED', 'CHANGED', 'NO_CHANGE', 'ERROR'
    last_comparison_time = db.Column(db.DateTime, nullable=True)
    change_detected = db.Column(db.Boolean, nullable=True)

    __table_args__ = (
        db.Index('idx_area_config_unique_key', 'area_config_id', 'unique_key'),
        db.Index('idx_unique_key_capture_time', 'unique_key', 'capture_time'), # To fetch latest efficiently
    )

    def to_dict(self):
        return {
            'id': self.id,
            'areaConfigId': self.area_config_id,
            'uniqueKey': self.unique_key,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'captureTime': self.capture_time.isoformat(),
            'imagePath': self.image_path,
            'status': self.status,
            'lastComparisonTime': self.last_comparison_time.isoformat() if self.last_comparison_time else None,
            'changeDetected': self.change_detected
        }

# --- New Models for Alert System ---
class AlertSession(db.Model):
    __tablename__ = 'alert_sessions'
    id = db.Column(db.Integer, primary_key=True)
    area_config_id = db.Column(db.Integer, db.ForeignKey('area_configs.id'), nullable=False)
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(50), nullable=False) # 'IN_PROGRESS', 'COMPLETED_CHANGES_DETECTED', 'COMPLETED_NO_CHANGES', 'COMPLETED_ERROR'
    total_changes_detected = db.Column(db.Integer, default=0)
    notification_sent = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            'id': self.id,
            'areaConfigId': self.area_config_id,
            'startTime': self.start_time.isoformat(),
            'endTime': self.end_time.isoformat() if self.end_time else None,
            'status': self.status,
            'totalChangesDetected': self.total_changes_detected,
            'notificationSent': self.notification_sent
        }

class AlertDetail(db.Model):
    __tablename__ = 'alert_details'
    id = db.Column(db.Integer, primary_key=True)
    alert_session_id = db.Column(db.Integer, db.ForeignKey('alert_sessions.id'), nullable=False)
    image_tile_id = db.Column(db.Integer, db.ForeignKey('image_tiles.id'), nullable=False)
    previous_image_path = db.Column(db.String(255), nullable=False)
    current_image_path = db.Column(db.String(255), nullable=False)
    change_log = db.Column(db.JSON, nullable=True) # JSON type for comparison result
    alert_time = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'alertSessionId': self.alert_session_id,
            'imageTileId': self.image_tile_id,
            'previousImagePath': self.previous_image_path,
            'currentImagePath': self.current_image_path,
            'changeLog': self.change_log,
            'alertTime': self.alert_time.isoformat()
        }
