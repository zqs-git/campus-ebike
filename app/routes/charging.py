from flask import Blueprint, request, jsonify
from datetime import datetime
from app import db
from app.models.charging import (
    ChargingPile,
    ChargingSession,
    ChargingPileStatus,
    ChargingSessionStatus
)
from app.models.location import CampusLocation

charging_bp = Blueprint('charging_api', __name__, url_prefix='/api')


@charging_bp.route('/charging_area/get_charging_areas', methods=['GET'])
def get_charging_areas():
    """获取所有充电区（CampusLocation.location_type=='charging'）"""
    areas = CampusLocation.query.filter_by(location_type='charging').all()
    return jsonify([
        {
            'id': area.id,
            'name': area.name,
            'latitude': area.latitude,
            'longitude': area.longitude
        } for area in areas
    ]), 200


@charging_bp.route('/charging-piles', methods=['GET'])
def get_charging_piles():
    """根据 location_id 获取某个充电区下的所有充电桩"""
    location_id = request.args.get('location_id', type=int)
    if not location_id:
        return jsonify({'error': 'location_id is required'}), 400

    piles = ChargingPile.query.filter_by(location_id=location_id).all()
    return jsonify([
        {
            'id': pile.id,
            'name': pile.name,
            'connector': pile.connector,
            'power_kw': pile.power_kw,
            'fee_rate': pile.fee_rate,
            'status': pile.status.value,
            'updated_at': pile.updated_at.isoformat()
        } for pile in piles
    ]), 200


@charging_bp.route('/charging-sessions/reserve', methods=['POST'])
def reserve_charging_session():
    """用户预约充电桩（创建 ChargingSession，并把 ChargingPile.status 设为 reserved）"""
    data = request.get_json() or {}
    user_id = data.get('user_id')
    pile_id = data.get('pile_id')
    if not user_id or not pile_id:
        return jsonify({'error': 'user_id and pile_id are required'}), 400

    # 检查桩状态
    pile = ChargingPile.query.get(pile_id)
    if not pile or pile.status is not ChargingPileStatus.available:
        return jsonify({'error': 'pile not available'}), 400

    # 创建会话
    session = ChargingSession(
        user_id=user_id,
        pile_id=pile_id,
        status=ChargingSessionStatus.reserved
    )
    db.session.add(session)

    # 更新桩状态
    pile.status = ChargingPileStatus.reserved
    db.session.commit()

    return jsonify({'message': '预约成功', 'session_id': session.id}), 201


@charging_bp.route('/charging-sessions/<int:session_id>/start', methods=['POST'])
def start_charging(session_id):
    """开始充电：将会话状态改为 ongoing，记录 start_time，并更新桩状态为 charging"""
    session = ChargingSession.query.get(session_id)
    if not session or session.status is not ChargingSessionStatus.reserved:
        return jsonify({'error': 'invalid session'}), 400

    session.start_time = datetime.utcnow()
    session.status = ChargingSessionStatus.ongoing

    pile = ChargingPile.query.get(session.pile_id)
    pile.status = ChargingPileStatus.charging

    db.session.commit()
    return jsonify({'message': '充电已开始'}), 200


@charging_bp.route('/charging-sessions/<int:session_id>/stop', methods=['POST'])
def stop_charging(session_id):
    """停止充电：计算电量 & 费用，更新会话和桩的状态"""
    session = ChargingSession.query.get(session_id)
    if not session or session.status is not ChargingSessionStatus.ongoing:
        return jsonify({'error': 'invalid session'}), 400

    session.end_time = datetime.utcnow()
    session.status = ChargingSessionStatus.completed

    # 计算充电量与费用
    duration_h = (session.end_time - session.start_time).total_seconds() / 3600.0
    pile     = ChargingPile.query.get(session.pile_id)
    session.energy_kwh = round(duration_h * pile.power_kw, 3)
    session.fee_amount = round(session.energy_kwh * pile.fee_rate, 2)

    # 恢复桩状态
    pile.status = ChargingPileStatus.available

    db.session.commit()
    return jsonify({
        'message': '充电已结束',
        'energy_kwh': session.energy_kwh,
        'fee_amount': session.fee_amount
    }), 200


# 管理员接口

# 创建充电区（CampusLocation）
# 充电区是一个地点，包含多个充电桩
# 充电区的名称、经纬度等信息
# 充电区的类型为 'charging'，在 CampusLocation 表中存储

@charging_bp.route('/charging_area/create', methods=['POST'])
def create_charging_area():
    data = request.get_json() or {}
    name = data.get('name')
    lat = data.get('latitude')
    lng = data.get('longitude')

    if not name or lat is None or lng is None:
        return jsonify({'error': 'name, latitude, longitude required'}), 400

    area = CampusLocation(name=name, latitude=lat, longitude=lng, location_type='charging')
    db.session.add(area)
    db.session.commit()
    return jsonify({'message': '创建成功', 'id': area.id}), 201

# 更新充电区信息
@charging_bp.route('/charging_area/<int:id>/update', methods=['PUT'])
def update_charging_area(id):
    area = CampusLocation.query.get(id)
    if not area:
        return jsonify({'error': '区域不存在'}), 404

    data = request.get_json() or {}
    area.name = data.get('name', area.name)
    area.latitude = data.get('latitude', area.latitude)
    area.longitude = data.get('longitude', area.longitude)
    db.session.commit()
    return jsonify({'message': '更新成功'}), 200

# 删除充电区
@charging_bp.route('/charging_area/<int:id>/delete', methods=['DELETE'])
def delete_charging_area(id):
    area = CampusLocation.query.get(id)
    if not area:
        return jsonify({'error': '区域不存在'}), 404

    db.session.delete(area)
    db.session.commit()
    return jsonify({'message': '已删除'}), 200


# 创建充电桩（ChargingPile）
@charging_bp.route('/charging-piles', methods=['POST'])
def create_charging_pile():
    data = request.get_json() or {}
    name = data.get('name')
    connector = data.get('connector')
    location_id = data.get('location_id')
    power_kw = data.get('power_kw')
    fee_rate = data.get('fee_rate')

    if not all([name, connector, location_id, power_kw, fee_rate]):
        return jsonify({'error': '缺少字段'}), 400

    pile = ChargingPile(
        name=name,
        connector=connector,
        location_id=location_id,
        power_kw=power_kw,
        fee_rate=fee_rate,
        status=ChargingPileStatus.available
    )
    db.session.add(pile)
    db.session.commit()
    return jsonify({'message': '充电桩创建成功', 'id': pile.id}), 201


# 删除充电桩
@charging_bp.route('/charging-piles/<int:id>', methods=['PUT'])
def update_charging_pile(id):
    pile = ChargingPile.query.get(id)
    if not pile:
        return jsonify({'error': '未找到充电桩'}), 404

    data = request.get_json() or {}
    pile.name = data.get('name', pile.name)
    pile.connector = data.get('connector', pile.connector)
    pile.power_kw = data.get('power_kw', pile.power_kw)
    pile.fee_rate = data.get('fee_rate', pile.fee_rate)
    db.session.commit()
    return jsonify({'message': '更新成功'}), 200

# 删除充电桩
@charging_bp.route('/charging-piles/<int:id>', methods=['DELETE'])
def delete_charging_pile(id):
    pile = ChargingPile.query.get(id)
    if not pile:
        return jsonify({'error': '充电桩不存在'}), 404

    db.session.delete(pile)
    db.session.commit()
    return jsonify({'message': '删除成功'}), 200


# 获取充电日志
@charging_bp.route('/charging-logs', methods=['GET'])
def get_charging_logs():
    logs = ChargingSession.query.order_by(ChargingSession.id.desc()).limit(100).all()
    result = []
    for log in logs:
        result.append({
            'id': log.id,
            'user_id': log.user_id,
            'pile_name': log.pile.name if log.pile else '未知',
            'user_name': log.user.username if hasattr(log.user, 'username') else f'UID:{log.user_id}',
            'start_time': log.start_time.isoformat() if log.start_time else '',
            'end_time': log.end_time.isoformat() if log.end_time else '',
            'energy_kwh': log.energy_kwh,
            'fee_amount': log.fee_amount
        })
    return jsonify(result), 200
