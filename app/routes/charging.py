from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta, date, time
from app import db
from app.models.charging import (
    ChargingPile,
    ChargingSession,
    ChargingPileStatus,
    ChargingSessionStatus
)
from app.models.location import CampusLocation
from app.models.vehicles import ElectricVehicle

charging_bp = Blueprint('charging_api', __name__, url_prefix='/api')


def _cleanup_expired_reservations():
    """把超过10分钟未开始的“reserved”会话，标记为 cancelled, 并释放桩"""
    cutoff = datetime.utcnow() - timedelta(minutes=10)
    expired = ChargingSession.query.filter(
        ChargingSession.status == ChargingSessionStatus.reserved,
        ChargingSession.created_at < cutoff
    ).all()
    for sess in expired:
        sess.status = ChargingSessionStatus.cancelled
        pile = ChargingPile.query.get(sess.pile_id)
        if pile:
            pile.status = ChargingPileStatus.available
    if expired:
        db.session.commit()


@charging_bp.route('/charging_area/get_charging_areas', methods=['GET'])
def get_charging_areas():
    areas = CampusLocation.query.filter_by(location_type='charging').all()
    return jsonify([{
        'id': area.id,
        'name': area.name,
        'latitude': area.latitude,
        'longitude': area.longitude
    } for area in areas]), 200


@charging_bp.route('/charging-piles', methods=['GET'])
def get_charging_piles():
    location_id = request.args.get('location_id', type=int)
    if not location_id:
        return jsonify({'error': 'location_id is required'}), 400
    piles = ChargingPile.query.filter_by(location_id=location_id).all()
    return jsonify([{
        'id': pile.id,
        'name': pile.name,
        'connector': pile.connector,
        'power_kw': pile.power_kw,
        'fee_rate': pile.fee_rate,
        'status': pile.status.value,
        'updated_at': pile.updated_at.isoformat()
    } for pile in piles]), 200


@charging_bp.route('/charging-sessions/reserve', methods=['POST'])
def reserve_charging_session():
    _cleanup_expired_reservations()
    data = request.get_json() or {}
    user_id    = data.get('user_id')
    pile_id    = data.get('pile_id')
    vehicle_id = data.get('vehicle_id')
    date_str   = data.get('date')        # YYYY-MM-DD
    start_str  = data.get('start_time')  # HH:MM
    end_str    = data.get('end_time')    # HH:MM

    # 验参
    if not all([user_id, pile_id, vehicle_id, date_str, start_str, end_str]):
        return jsonify({'error': '缺少 user_id/pile_id/vehicle_id/date/start_time/end_time'}), 400

    # 解析日期与时间
    try:
        res_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        t_start  = datetime.strptime(start_str, '%H:%M').time()
        t_end    = datetime.strptime(end_str, '%H:%M').time()
    except ValueError:
        return jsonify({'error': '时间格式错误'}), 400

    # 计算起止 datetime，若 end_time ≤ start_time，则视为跨到下一天
    dt_start = datetime.combine(res_date, t_start)
    if t_end <= t_start:
        dt_end = datetime.combine(res_date + timedelta(days=1), t_end)
    else:
        dt_end = datetime.combine(res_date, t_end)

    # 校验：开始必须在未来，且结束必须在开始之后
    now_utc = datetime.utcnow()
    if dt_start <= now_utc or dt_end <= dt_start:
        return jsonify({'error': '无效的时间区间'}), 400

    # 用户与桩校验
    ev   = ElectricVehicle.query.filter_by(id=vehicle_id, owner_id=user_id).first()
    pile = ChargingPile.query.get(pile_id)
    if not ev or not pile:
        return jsonify({'error': '车辆或充电桩不存在'}), 400

    # 冲突检查：是否有预约区间重叠
    conflict = ChargingSession.query.filter(
        ChargingSession.pile_id == pile_id,
        ChargingSession.status != ChargingSessionStatus.cancelled,
        # 已存的 start/end 与新范围有交集
        ChargingSession.reserved_start_time < t_end,
        ChargingSession.reserved_end_time   > t_start
    ).first()
    if conflict:
        return jsonify({'error': '该时段区间已被占用'}), 400

    # 创建完整区间预约
    session = ChargingSession(
        user_id               = user_id,
        pile_id               = pile_id,
        vehicle_id            = vehicle_id,
        slot_time             = dt_start,
        reserved_date         = res_date,
        reserved_start_time   = t_start,
        reserved_end_time     = t_end,
        status                = ChargingSessionStatus.reserved
    )
    db.session.add(session)
    pile.status = ChargingPileStatus.reserved
    db.session.commit()

    return jsonify({'message': '预约成功', 'session_id': session.id}), 201


@charging_bp.route('/charging-sessions/<int:session_id>/cancel', methods=['POST'])
def cancel_charging_session(session_id):
    _cleanup_expired_reservations()
    session = ChargingSession.query.get(session_id)
    if not session or session.status != ChargingSessionStatus.reserved:
        return jsonify({'error': '无效的会话，无法取消'}), 400
    session.status = ChargingSessionStatus.cancelled
    pile = ChargingPile.query.get(session.pile_id)
    if pile:
        pile.status = ChargingPileStatus.available
    db.session.commit()
    return jsonify({'message': '取消成功'}), 200


@charging_bp.route('/charging-sessions/<int:session_id>/start', methods=['POST'])
def start_charging(session_id):
    session = ChargingSession.query.get(session_id)
    if not session or session.status != ChargingSessionStatus.reserved:
        return jsonify({'error': 'invalid session'}), 400
    session.start_time = datetime.utcnow()
    session.status     = ChargingSessionStatus.ongoing
    pile = ChargingPile.query.get(session.pile_id)
    pile.status = ChargingPileStatus.charging
    db.session.commit()
    return jsonify({'message': '充电已开始'}), 200


@charging_bp.route('/charging-sessions/<int:session_id>/stop', methods=['POST'])
def stop_charging(session_id):
    session = ChargingSession.query.get(session_id)
    if not session or session.status != ChargingSessionStatus.ongoing:
        return jsonify({'error': 'invalid session'}), 400
    session.end_time = datetime.utcnow()
    session.status   = ChargingSessionStatus.completed
    duration_h = (session.end_time - session.start_time).total_seconds() / 3600.0
    pile      = ChargingPile.query.get(session.pile_id)
    session.energy_kwh = round(duration_h * pile.power_kw, 3)
    session.fee_amount = round(session.energy_kwh * pile.fee_rate, 2)
    pile.status = ChargingPileStatus.available
    db.session.commit()
    return jsonify({'message': '充电已结束', 'energy_kwh': session.energy_kwh, 'fee_amount': session.fee_amount}), 200


# 管理员接口

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


@charging_bp.route('/charging_area/<int:id>/delete', methods=['DELETE'])
def delete_charging_area(id):
    area = CampusLocation.query.get(id)
    if not area:
        return jsonify({'error': '区域不存在'}), 404

    db.session.delete(area)
    db.session.commit()
    return jsonify({'message': '已删除'}), 200


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


@charging_bp.route('/charging-piles/<int:id>', methods=['DELETE'])
def delete_charging_pile(id):
    pile = ChargingPile.query.get(id)
    if not pile:
        return jsonify({'error': '充电桩不存在'}), 404

    db.session.delete(pile)
    db.session.commit()
    return jsonify({'message': '删除成功'}), 200


from flask import jsonify
from sqlalchemy.orm import joinedload

@charging_bp.route('/charging-logs', methods=['GET'])
def get_charging_logs():
    # 一次性把 user、pile 以及 pile.location 都加载进来
    logs = (ChargingSession.query
            .options(
                joinedload(ChargingSession.user),
                joinedload(ChargingSession.pile).joinedload(ChargingPile.location)
            )
            .order_by(ChargingSession.id.desc())
            .limit(100)
            .all())

    result = []
    for log in logs:
        result.append({
            'id': log.id,
            'user_id': log.user_id,
            # 用户名
            'user_name': log.user.name if log.user and log.user.name else f'UID:{log.user_id}',
            # 车辆ID
            'vehicle_id': log.vehicle_id,
            # 充电桩名称
            'pile_name': log.pile.name if log.pile else '未知桩',
            # 充电区／位置名称
            'charging_zone': (log.pile.location.name 
                              if log.pile and log.pile.location and hasattr(log.pile.location, 'name') 
                              else f'LOC:{log.pile.location_id}' if log.pile else '未知区域'),
            'start_time': log.start_time.isoformat() if log.start_time else '',
            'end_time':   log.end_time.isoformat()   if log.end_time   else '',
            'energy_kwh': log.energy_kwh,
            'fee_amount': log.fee_amount
        })

    return jsonify(result), 200



@charging_bp.route('/charging-piles/<int:pile_id>/slots', methods=['GET'])
def get_pile_slots(pile_id):
    _cleanup_expired_reservations()

    date_str = request.args.get('date')
    user_id  = request.args.get('user_id', type=int)
    if not date_str:
        return jsonify({'error': 'date 参数必填，格式 YYYY-MM-DD'}), 400

    try:
        day_start = datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        return jsonify({'error': 'date 格式应为 YYYY-MM-DD'}), 400

    # 生成未来 72 个 20 分钟粒度的 slot
    slots = []
    now_utc = datetime.utcnow()
    for i in range(72):
        slot_dt = day_start + timedelta(minutes=20 * i)
        if slot_dt > now_utc:
            slots.append({'slot_time': slot_dt})

    # 拉当天所有未取消的会话
    sessions = ChargingSession.query.filter(
        ChargingSession.pile_id   == pile_id,
        ChargingSession.slot_time >= day_start,
        ChargingSession.slot_time <  day_start + timedelta(days=1),
        ChargingSession.status    != ChargingSessionStatus.cancelled
    ).all()

    result = []
    for s in slots:
        st = 'free'
        owner = None

        # 判断每个 20 分钟格子是否落在某个预约区间内（支持跨日）
        for sess in sessions:
            start_dt = datetime.combine(sess.reserved_date, sess.reserved_start_time)
            if sess.reserved_end_time <= sess.reserved_start_time:
                end_dt = datetime.combine(sess.reserved_date + timedelta(days=1), sess.reserved_end_time)
            else:
                end_dt = datetime.combine(sess.reserved_date, sess.reserved_end_time)

            if start_dt <= s['slot_time'] < end_dt:
                if sess.status == ChargingSessionStatus.reserved:
                    st = ('mine' if (user_id and sess.user_id == user_id)
                          else 'reserved')
                else:
                    st = 'occupied'
                owner = sess.user_id
                break

        result.append({
            'slot':            s['slot_time'].strftime('%H:%M'),
            'status':          st,
            'session_id':      sess.id if owner else None,
            'session_user_id': owner
        })

    return jsonify(result), 200


@charging_bp.route('/charging-sessions/user/<int:user_id>', methods=['GET'])
def get_my_reservations(user_id):
    _cleanup_expired_reservations()
    sessions = ChargingSession.query.filter(
        ChargingSession.user_id == user_id,
        ChargingSession.status.in_([
            ChargingSessionStatus.reserved,
            ChargingSessionStatus.ongoing
        ])
    ).all()

    result = []
    for s in sessions:
        result.append({
            'session_id': s.id,
            'pile_id':    s.pile_id,
            'pile_name':  s.pile.name,
            'date':       s.reserved_date.isoformat(),
            'start_slot': s.reserved_start_time.strftime('%H:%M'),
            'end_slot':   s.reserved_end_time.strftime('%H:%M'),
            'status':     s.status.value
        })
    return jsonify(result), 200
