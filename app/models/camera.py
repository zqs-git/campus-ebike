from app import db
from datetime import datetime

class Camera(db.Model):
    __tablename__ = 'camera'
    id          = db.Column(db.Integer, primary_key=True)
    location_id = db.Column(db.Integer, db.ForeignKey('campus_locations.id'), nullable=False)
    name        = db.Column(db.String(100), nullable=False)
    rtsp_url    = db.Column(db.String(255), nullable=True)

class Violation(db.Model):
    __tablename__ = 'violation'
    id           = db.Column(db.Integer, primary_key=True)
    camera_id    = db.Column(db.Integer, db.ForeignKey('camera.id'), nullable=False)
    zone_id      = db.Column(db.Integer, nullable=False)
    plate_number = db.Column(db.String(32), nullable=False)
    image_path   = db.Column(db.String(255))
    occurred_at  = db.Column(db.DateTime, nullable=False)
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)
