from flask import Blueprint, jsonify, request
from app import db
from app.models.location import CampusLocation

location_bp = Blueprint('location', __name__, url_prefix='/api/location')

# 查看所有地点
@location_bp.route('/get_location', methods=['GET'])
def get_locations():
    locations = CampusLocation.query.all()
    return jsonify([{
        'id': loc.id,
        'name': loc.name,
        'latitude': loc.latitude,
        'longitude': loc.longitude,
        'location_type': loc.location_type,
        'description': loc.description,
        'created_at': loc.created_at
    } for loc in locations]), 200

# 查看单个地点
@location_bp.route('/get_location/<int:location_id>', methods=['GET'])
def get_location(location_id):
    location = CampusLocation.query.get(location_id)
    if not location:
        return jsonify({"message": "地点不存在"}), 404
    return jsonify({
        'id': location.id,
        'name': location.name,
        'latitude': location.latitude,
        'longitude': location.longitude,
        'location_type': location.location_type,
        'description': location.description,
        'created_at': location.created_at
    }), 200

# 创建地点
@location_bp.route('/add_location', methods=['POST'])
def add_location():
    data = request.get_json()
    name = data['name']
    latitude = data['latitude']
    longitude = data['longitude']
    location_type = data.get('location_type', 'other')
    description = data.get('description', '')

    location = CampusLocation(
        name=name,
        latitude=latitude,
        longitude=longitude,
        location_type=location_type,
        description=description
    )
    db.session.add(location)
    db.session.commit()

    return jsonify({"message": "地点创建成功", "location_id": location.id}), 201

# 修改地点
@location_bp.route('/update_location/<int:location_id>', methods=['PUT'])
def update_location(location_id):
    location = CampusLocation.query.get(location_id)
    if not location:
        return jsonify({"message": "地点不存在"}), 404

    data = request.get_json()
    location.name = data.get('name', location.name)
    location.latitude = data.get('latitude', location.latitude)
    location.longitude = data.get('longitude', location.longitude)
    location.location_type = data.get('location_type', location.location_type)
    location.description = data.get('description', location.description)

    db.session.commit()
    return jsonify({"message": "地点更新成功"}), 200

# 删除地点
@location_bp.route('/delete_location/<int:location_id>', methods=['DELETE'])
def delete_location(location_id):
    location = CampusLocation.query.get(location_id)
    if not location:
        return jsonify({"message": "地点不存在"}), 404

    db.session.delete(location)
    db.session.commit()
    return jsonify({"message": "地点删除成功"}), 200

# 根据地点类型查看地点
@location_bp.route('/get_locations/type/<location_type>', methods=['GET'])
def get_locations_by_type(location_type):
    locations = CampusLocation.query.filter_by(location_type=location_type).all()
    if not locations:
        return jsonify({"message": "没有找到此类型的地点"}), 404
    
    return jsonify([{
        'id': loc.id,
        'name': loc.name,
        'latitude': loc.latitude,
        'longitude': loc.longitude,
        'location_type': loc.location_type,
        'description': loc.description,
        'created_at': loc.created_at
    } for loc in locations]), 200



from flask import Blueprint, request, jsonify, abort
from app import db
from app.models.location import CampusLocation
from sqlalchemy.exc import SQLAlchemyError

locations_bp = Blueprint('locations', __name__, url_prefix='/api/areas')

# -----------------------------------
# 模型示例（app/models/location.py）
# -----------------------------------
# class CampusLocation(db.Model):
#     id             = db.Column(db.Integer, primary_key=True)
#     name           = db.Column(db.String(128), nullable=False)
#     latitude       = db.Column(db.Float, nullable=False)
#     longitude      = db.Column(db.Float, nullable=False)
#     location_type  = db.Column(db.String(32), nullable=False)
#     # JSON 类型字段，用来存储 [[lng, lat], ...] 这类列表
#     path           = db.Column(db.JSON, nullable=False)  
#     created_at     = db.Column(db.DateTime, server_default=db.func.now())
# -----------------------------------

# GET /api/areas
@locations_bp.route('', methods=['GET'])
def get_areas():
    areas = CampusLocation.query.order_by(CampusLocation.created_at).all()
    payload = []
    for a in areas:
        payload.append({
            'id': a.id,
            'name': a.name,
            'path': a.path,  
            'center': { 'lng': a.longitude, 'lat': a.latitude },
            'type': a.location_type
        })
    return jsonify(payload), 200

# GET /api/areas/<id>
@locations_bp.route('/<int:area_id>', methods=['GET'])
def get_area(area_id):
    a = CampusLocation.query.get_or_404(area_id)
    return jsonify({
        'id': a.id,
        'name': a.name,
        'path': a.path,
        'center': { 'lng': a.longitude, 'lat': a.latitude },
        'type': a.location_type
    }), 200

# POST /api/areas
@locations_bp.route('', methods=['POST'])
def create_area():
    data = request.get_json() or {}
    name     = data.get('name')
    path     = data.get('path')      # [[lng, lat], ...]
    center   = data.get('center')    # 可能是 dict、也可能是 list、甚至 None
    loc_type = data.get('type')
    # 前端也可能直接传 latitude/longitude
    lat_val  = data.get('latitude')
    lng_val  = data.get('longitude')

    # 如果 center 是 list → 转成 dict
    if isinstance(center, list) and len(center) >= 2:
        center = {'lng': center[0], 'lat': center[1]}

    # 如果 center 还是不是 dict，就 fallback 到 latitude/longitude
    if not isinstance(center, dict):
        center = {'lng': lng_val, 'lat': lat_val}

    # 必填验证
    if not all([
        name,
        isinstance(path, list) and len(path) > 0,
        center.get('lat') is not None,
        center.get('lng') is not None,
        loc_type
    ]):
        abort(400, '缺少 name, path, center 或 type 字段')

    try:
        a = CampusLocation(
            name           = name,
            latitude       = center['lat'],
            longitude      = center['lng'],
            location_type  = loc_type,
            path           = path
        )
        db.session.add(a)
        db.session.commit()
        return jsonify({ 'id': a.id }), 201

    except SQLAlchemyError as e:
        db.session.rollback()
        abort(500, f'数据库错误：{e}')


# DELETE /api/areas/<id>
@locations_bp.route('/<int:area_id>', methods=['DELETE'])
def delete_area(area_id):
    a = CampusLocation.query.get_or_404(area_id)
    try:
        db.session.delete(a)
        db.session.commit()
        return '', 204
    except SQLAlchemyError as e:
        db.session.rollback()
        abort(500, f'数据库错误：{e}')
