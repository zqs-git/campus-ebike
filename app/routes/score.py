from flask import Blueprint, request, jsonify
from sqlalchemy import or_,func
from datetime import datetime
from sqlalchemy import func, and_
# from . import serialize

from app.extensions import db
from app.models.score import ScoreRule, ScoreLog, ReportedEvent, Appeal,Violation
from app.models.users import User
from app.models.vehicles import ElectricVehicle

score_bp = Blueprint('score', __name__, url_prefix='/api/score')

def serialize(model, fields):
    """通用序列化：把指定字段抽取成 dict，datetime 自动 isoformat"""
    data = {}
    for field in fields:
        val = getattr(model, field)
        if isinstance(val, datetime):
            data[field] = val.isoformat()
        else:
            data[field] = val
    return data

# —— ScoreRule CRUD ——

@score_bp.route('/rules', methods=['GET'])
def list_rules():
    rules = ScoreRule.query.order_by(ScoreRule.id).all()
    return jsonify([r.to_dict() for r in rules])



@score_bp.route('/rules', methods=['POST'])
def create_rule():
    data = request.json or {}
    rule = ScoreRule(**data)
    db.session.add(rule)
    db.session.commit()
    return jsonify(rule.to_dict()), 201

@score_bp.route('/rules/<int:id>', methods=['PUT'])
def update_rule(id):
    data = request.json or {}
    rule = ScoreRule.query.get_or_404(id)
    for key, val in data.items():
        setattr(rule, key, val)
    rule.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify(rule.to_dict())

@score_bp.route('/rules/<int:id>', methods=['DELETE'])
def delete_rule(id):
    rule = ScoreRule.query.get_or_404(id)
    db.session.delete(rule)
    db.session.commit()
    return '', 204

# —— 自动加减分日志 ——
@score_bp.route('/auto-logs', methods=['GET'])
def auto_logs():
    logs = ScoreLog.query.order_by(ScoreLog.timestamp.desc()).all()
    fields = ['id', 'user_id', 'license_plate', 'event_type', 'points', 'timestamp','source']
    return jsonify([serialize(l, fields) for l in logs])

# —— 上报事件审核 ——
@score_bp.route('/reports/pending', methods=['GET'])
def pending_reports():
    """
    获取待审核的用户上报事件列表
    """
    evs = ReportedEvent.query.filter_by(status='pending') \
                              .order_by(ReportedEvent.created_at.desc()) \
                              .all()

    result = []
    # 指定要返回的字段
    fields = ['id', 'reporter_id', 'license_plate', 'event_type', 'details', 'status', 'created_at', 'adjust_points']
    for e in evs:
        item = serialize(e, fields)
        # 再加上人性化的上报人名字
        reporter = User.query.get(e.reporter_id)
        item['reporter'] = reporter.name if reporter else None
        result.append(item)

    return jsonify(result), 200

@score_bp.route('/reports/<int:id>/approve', methods=['POST'])
def approve_report(id):
    data = request.json or {}
    e = ReportedEvent.query.get_or_404(id)
    e.status = 'approved'
    points = data.get('points', 0)
    e.adjust_points = points
    # 写入积分日志
    log = ScoreLog(
        user_id=e.reporter_id,
        license_plate=e.license_plate,
        event_type=e.event_type,
        points=points,
        source='report'
    )
    db.session.add(log)
    if user := User.query.get(log.user_id):
        user.score = (user.score or 0) + log.points
    db.session.commit()
    return '', 204

@score_bp.route('/reports/<int:id>/reject', methods=['POST'])
def reject_report(id):
    e = ReportedEvent.query.get_or_404(id)
    e.status = 'rejected'
    db.session.commit()
    return '', 204


## —— 学生端：发起违规上报 —— 
@score_bp.route('/reports', methods=['POST'])
def create_report():
    """
    学生端提交一条上报事件
    """
    data = request.json or {}
    reporter_id   = data.get('reporter_id')
    license_plate = data.get('license_plate')
    event_type    = data.get('event_type')
    details       = data.get('details', '')

    if not (reporter_id and license_plate and event_type):
        return jsonify({'msg':'reporter_id、license_plate、event_type 必填'}), 400

    e = ReportedEvent(
        reporter_id=reporter_id,
        license_plate=license_plate,
        event_type=event_type,
        details=details,
        status='pending',
        created_at=datetime.utcnow()
    )
    db.session.add(e)
    db.session.commit()

    # 用 serialize 返回刚创建的记录
    fields = ['id', 'reporter_id', 'license_plate', 'event_type', 'details', 'status', 'created_at']
    return jsonify(serialize(e, fields)), 201

# —— 申诉管理 ——
@score_bp.route('/appeals', methods=['GET'])
def list_appeals():
    """
    获取所有申诉记录
    """
    aps = Appeal.query.order_by(Appeal.created_at.desc()).all()
    fields = ['id', 'user_id', 'score_log_id', 'license_plate', 'event_type', 
              'reason', 'status', 'rejection_reason', 'created_at']
    
    result = []
    for a in aps:
        item = serialize(a, fields)
        # 添加用户名称
        user = User.query.get(a.user_id)
        item['user_name'] = user.name if user else None
        
        # 添加原始记录信息
        if a.score_log_id:
            log = ScoreLog.query.get(a.score_log_id)
            if log:
                item['original_points'] = log.points
                item['log_timestamp'] = log.timestamp.isoformat()
        
        result.append(item)
    
    return jsonify(result), 200


@score_bp.route('/appeals/<int:id>', methods=['POST'])
def handle_appeal(id):
    data = request.json or {}
    a = Appeal.query.get_or_404(id)
    approve = data.get('approve', False)
    
    if approve:
        # 申诉通过逻辑
        a.status = 'approved'
        a.rejection_reason = None  # 清除可能存在的驳回原因
        
        # 查找原始扣分记录
        original_log = ScoreLog.query.get(a.score_log_id)
        if original_log:
            # 创建一个反向积分记录来抵消原扣分
            reverse_points = abs(original_log.points)
            
            # 创建积分日志
            log = ScoreLog(
                user_id=a.user_id,
                license_plate=a.license_plate,
                event_type=f"申诉通过: {a.event_type}",  # 更清晰的事件类型描述
                points=reverse_points,
                source='appeal'
            )
            db.session.add(log)
            
            # 更新用户积分
            if user := User.query.get(a.user_id):
                user.score = (user.score or 0) + reverse_points
    else:
        # 申诉驳回逻辑
        a.status = 'rejected'
        
        # 保存驳回原因
        rejection_reason = data.get('rejection_reason', '').strip()
        if not rejection_reason:
            rejection_reason = "申诉未被批准"  # 默认驳回原因
        a.rejection_reason = rejection_reason
        
        # 可选：记录一条驳回日志（不影响积分）
        log = ScoreLog(
            user_id=a.user_id,
            license_plate=a.license_plate,
            event_type=f"申诉驳回: {a.event_type}",
            points=0,  # 驳回不改变积分
            source='appeal'
        )
        db.session.add(log)
    
    db.session.commit()
    return '', 204



## —— 学生端：提交扣分申诉 —— 
@score_bp.route('/appeals', methods=['POST'])
def create_appeal():
    """
    学生端提交一条申诉
    """
    data = request.json or {}
    user_id = data.get('user_id')
    score_log_id = data.get('score_log_id')  # 修改为 score_log_id
    reason = (data.get('reason') or '').strip()
    
    if not (user_id and score_log_id and reason):
        return jsonify({'msg':'user_id、score_log_id、reason 必填'}), 400
    
    # 检查对应的扣分记录是否存在
    score_log = ScoreLog.query.get(score_log_id)
    if not score_log:
        return jsonify({'msg':'对应的扣分记录不存在'}), 404
    
    # 创建申诉记录
    a = Appeal(
        user_id=user_id,
        score_log_id=score_log_id,  # 使用新字段
        license_plate=data.get('license_plate', score_log.license_plate),  # 优先使用传入的，否则使用记录中的
        event_type=data.get('event_type', score_log.event_type),  # 同上
        reason=reason,
        status='pending',
        created_at=datetime.utcnow()
    )
    db.session.add(a)
    db.session.commit()

    fields = ['id', 'user_id', 'score_log_id', 'license_plate', 'event_type', 'reason', 'status', 'created_at']
    return jsonify(serialize(a, fields)), 201


# —— 手动加减分 ——
@score_bp.route('/adjust', methods=['POST'])
def manual_adjust():
    data = request.json or {}
    user_id = data.get('user_id')
    points  = data.get('points')
    # 把 trim() 换成 strip()
    reason  = data.get('reason', '').strip()

    if user_id is None or points is None or not reason:
        return jsonify({"msg": "user_id、points 和 reason 都是必填项"}), 400

    log = ScoreLog(
        user_id=user_id,
        license_plate=data.get('license_plate'),
        event_type=reason,
        points=points,
        source='manual'
    )
    db.session.add(log)
    if user := User.query.get(log.user_id):
        user.score = (user.score or 0) + log.points
    db.session.commit()
    return jsonify({"id": log.id}), 201


# —— 用户搜索（供手动加减分使用） ——
@score_bp.route('/users/search', methods=['GET'])
def search_users():
    q = request.args.get('q', '').strip()
    if not q:
        return jsonify([])
    users = User.query.filter(
        or_(
            User.name.ilike(f'%{q}%'),
            User.phone.ilike(f'%{q}%'),
            User.school_id.ilike(f'%{q}%'),
            User.license_plate.ilike(f'%{q}%')
        )
    ).all()
    return jsonify([u.to_dict() for u in users])

@score_bp.route('/users/scores', methods=['GET'])
def list_users_with_scores():
    # 1) 子查询：每个用户最新的电动车记录 ID
    latest_ev = (
        db.session.query(
            ElectricVehicle.owner_id.label('owner_id'),
            func.max(ElectricVehicle.id).label('max_ev_id')
        )
        .group_by(ElectricVehicle.owner_id)
        .subquery()
    )

    # 2) 再把这条记录 join 回来，取出 plate_number
    plate_subq = (
        db.session.query(
            ElectricVehicle.owner_id.label('owner_id'),
            ElectricVehicle.plate_number.label('license_plate')
        )
        .join(latest_ev, ElectricVehicle.id == latest_ev.c.max_ev_id)
        .subquery()
    )

    # 3) 主查询：User + plate + 积分聚合
    rows = (
        db.session.query(
            User.id.label('user_id'),
            User.name,
            User.phone,
            plate_subq.c.license_plate,
            func.coalesce(func.sum(ScoreLog.points), 0).label('current_score')
        )
        .outerjoin(ScoreLog, ScoreLog.user_id == User.id)
        .outerjoin(plate_subq, plate_subq.c.owner_id == User.id)
        .group_by(
            User.id,
            User.name,
            User.phone,
            plate_subq.c.license_plate
        )
        .all()
    )

    # 序列化输出
    result = [
        {
            'user_id':       r.user_id,
            'name':          r.name,
            'phone':         r.phone,
            'license_plate': r.license_plate or '',
            'current_score': r.current_score
        }
        for r in rows
    ]
    return jsonify(result)

@score_bp.route('/users/<int:user_id>/logs', methods=['GET'])
def get_user_logs(user_id):
    # 左外联 Appeal，并且只联当前用户的那条申诉
    rows = (
        db.session.query(
            ScoreLog.id,
            ScoreLog.license_plate,
            ScoreLog.event_type,
            ScoreLog.points,
            ScoreLog.source,
            ScoreLog.timestamp,
            Appeal.status.label('appeal_status'),
            Appeal.rejection_reason
        )
        .outerjoin(
            Appeal,
            and_(
                Appeal.score_log_id == ScoreLog.id,
                Appeal.user_id == user_id
            )
        )
        .filter(ScoreLog.user_id == user_id)
        .order_by(ScoreLog.timestamp.desc())
        .all()
    )

    result = []
    for r in rows:
        result.append({
            'id':               r.id,
            'license_plate':    r.license_plate,
            'event_type':       r.event_type,
            'points':           r.points,
            'source':           r.source,
            'timestamp':        r.timestamp.isoformat(),
            # 这两个字段：没有申诉记录时，appeal_status 直接是 None
            'appeal_status':    r.appeal_status,        
            'rejection_reason': r.rejection_reason or '' 
        })
    return jsonify(result), 200

# app/routes/score.py (继续使用同一个 score_bp)

from app.models.score import Violation

# —— 违规记录审核 —— 
@score_bp.route('/violations/pending', methods=['GET'])
def pending_violations():
    """
    获取待审核的自动检测违规列表
    """
    vs = Violation.query.filter_by(status='pending') \
                        .order_by(Violation.timestamp.desc()) \
                        .all()
    fields = ['id', 'user_id', 'license_plate', 'event_type', 'location', 'timestamp', 'status']
    return jsonify([serialize(v, fields) for v in vs]), 200


@score_bp.route('/violations/<int:id>/approve', methods=['POST'])
def approve_violation(id):
    v = Violation.query.get_or_404(id)
    v.status = 'approved'
    # 审核通过后，生成扣分或加分日志
    # 找规则
    rule = ScoreRule.query.filter_by(event_type=v.event_type).first()
    pts = rule.points if rule else 0
    log = ScoreLog(
        user_id=v.user_id,
        license_plate=v.license_plate,
        event_type=v.event_type,
        points=pts,
        source='auto'  # 或 'report' / 'manual' 视场景
    )
    db.session.add(log)
    if user := User.query.get(log.user_id):
        user.score = (user.score or 0) + log.points
    db.session.commit()
    return '', 204

@score_bp.route('/violations/<int:id>/reject', methods=['POST'])
def reject_violation(id):
    v = Violation.query.get_or_404(id)
    v.status = 'rejected'
    db.session.commit()
    return '', 204
