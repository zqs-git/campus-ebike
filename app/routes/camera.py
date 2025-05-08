# backend/camera.py

from flask import Blueprint, request, jsonify
from flask_socketio import SocketIO
from app import db, socketio
from app.models.camera import  Camera, Violation
from app.models.location import CampusLocation
from datetime import datetime

camera_bp = Blueprint('camera_bp', __name__)

@camera_bp.route('/api/zones', methods=['GET'])
def get_zones():
    """
    返回所有类型为 'no-parking'（禁停区）的 CampusLocation，
    payload: [{ id, name, path: [...多边形顶点...] }, …]
    """
    rows = CampusLocation.query.filter_by(location_type='no-parking').all()
    zones = [
        {"id": r.id, "name": r.name, "path": r.path}
        for r in rows
    ]
    return jsonify(zones), 200

@camera_bp.route('/api/cameras', methods=['GET', 'POST'])
def manage_cameras():
    """
    可选：列出或新增摄像头配置
    GET  返回 [{ id, location_id, name, rtsp_url }, …]
    POST 新增 { location_id, name, rtsp_url }
    """
    if request.method == 'GET':
        cams = Camera.query.all()
        data = [
            {"id": c.id, "location_id": c.location_id, "name": c.name, "rtsp_url": c.rtsp_url}
            for c in cams
        ]
        return jsonify(data), 200

    # POST
    body = request.json
    cam = Camera(
        location_id=body['location_id'],
        name=body['name'],
        rtsp_url=body.get('rtsp_url')
    )
    db.session.add(cam)
    db.session.commit()
    return jsonify({"id": cam.id}), 201

@camera_bp.route('/api/violations', methods=['POST'])
def receive_violation():
    """
    接收检测服务上报的违停信息，存库并广播给所有 WebSocket 客户端
    请求 JSON: { camera_id, zone_id, plate_number, image_path, occurred_at }
    """
    data = request.get_json()
    v = Violation(
        camera_id    = data['camera_id'],
        zone_id      = data['zone_id'],
        plate_number = data['plate_number'],
        image_path   = data['image_path'],
        occurred_at  = datetime.fromisoformat(data['occurred_at'])
    )
    db.session.add(v)
    db.session.commit()

    # 通过 SocketIO 广播
    payload = {
        "camera_id":    v.camera_id,
        "zone_id":      v.zone_id,
        "plate_number": v.plate_number,
        "image_path":   v.image_path,
        "occurred_at":  v.occurred_at.isoformat()
    }
    socketio.emit('violation:new', payload)
    return jsonify(status='ok'), 201
