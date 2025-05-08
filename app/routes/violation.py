from flask import Blueprint, request, jsonify
from datetime import datetime
import random

from app import db
from app.models.score import Violation, ScoreRule, ScoreLog
from app.models.users import User
from app.models.vehicles import ElectricVehicle

violation_bp = Blueprint('violations', __name__, url_prefix='/api/violations')

@violation_bp.route('/simulate', methods=['POST'])
def simulate_violation():
    """
    单条模拟生成违规记录，并根据规则自动扣分或加分，生成 ScoreLog
    接收 JSON: { user_id, license_plate, event_type, location }
    返回: 新建的 violation 记录
    """
    data = request.get_json() or {}
    user_id = data.get('user_id')
    license_plate = data.get('license_plate')
    event_type = data.get('event_type')
    location = data.get('location', '')

    # 校验
    if not user_id or not license_plate or not event_type:
        return jsonify({'message': '参数不全'}), 400

    # 查扣分/加分规则
    rule = ScoreRule.query.filter_by(event_type=event_type).first()
    if not rule:
        return jsonify({'message': '未知的事件类型'}), 400

    # 查车辆
    vehicle = ElectricVehicle.query.filter_by(plate_number=license_plate).first()

    # 创建违规记录，直接设为 approved
    violation = Violation(
        user_id=user_id,
        vehicle_id=vehicle.id if vehicle else None,
        license_plate=license_plate,
        event_type=event_type,
        location=location,
        timestamp=datetime.utcnow(),
        status='approved'
    )
    db.session.add(violation)

    # 更新用户积分（直接加上规则定义的 points，可正可负）
    user = User.query.get(user_id)
    if not user:
        db.session.rollback()
        return jsonify({'message': '用户不存在'}), 404
    user.score = (user.score or 0) + rule.points

    # 记录积分变动，points 字段使用 rule.points
    log = ScoreLog(
        user_id=user_id,
        vehicle_id=vehicle.id if vehicle else None,
        license_plate=license_plate,
        event_type=event_type,
        points=rule.points,
        source='auto',
        timestamp=datetime.utcnow()
    )
    db.session.add(log)
    db.session.commit()

    return jsonify(violation.to_dict()), 201


@violation_bp.route('/simulate/batch', methods=['POST'])
def simulate_batch():
    """
    批量生成模拟违规记录
    接收 JSON: { count: int, useOnlyRealUsers: bool }
    返回: 生成条数
    """
    data = request.get_json() or {}
    count = data.get('count', 10)
    use_only_real = data.get('useOnlyRealUsers', False)

    # 获取规则
    rules = ScoreRule.query.all()
    if not rules:
        return jsonify({'message': '没有可用的扣分规则'}), 400

    # 获取车辆
    query = ElectricVehicle.query
    if use_only_real:
        query = query.filter(ElectricVehicle.owner_id.isnot(None))
    vehicles = query.all()
    if not vehicles:
        return jsonify({'message': '没有车辆数据可用'}), 400

    created = []
    for i in range(int(count)):
        vehicle = random.choice(vehicles)
        rule = random.choice(rules)

        v = Violation(
            user_id=vehicle.owner_id,
            vehicle_id=vehicle.id,
            license_plate=vehicle.plate_number,
            event_type=rule.event_type,
            location=f"模拟地点{i+1}",
            timestamp=datetime.utcnow(),
            status='approved'
        )
        db.session.add(v)

        # 更新用户积分
        user = User.query.get(vehicle.owner_id)
        if user:
            user.score = (user.score or 0) + rule.points

        # 记录积分变动
        log = ScoreLog(
            user_id=vehicle.owner_id,
            vehicle_id=vehicle.id,
            license_plate=vehicle.plate_number,
            event_type=rule.event_type,
            points=rule.points,
            source='auto',
            timestamp=datetime.utcnow()
        )
        db.session.add(log)
        created.append(v)

    db.session.commit()
    return jsonify({'message': f'成功生成 {len(created)} 条模拟违规'}), 201
