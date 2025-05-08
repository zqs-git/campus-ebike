# app/models/score.py

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Enum

from app import db
from datetime import datetime

class ScoreRule(db.Model):
    """
    积分规则表：系统中所有自动或手动的加减分规则都存这里。
    管理员可以增删改这些规则。
    """
    __tablename__ = 'score_rules'

    id = db.Column(
        db.Integer,
        primary_key=True,
        comment="主键，自增"
    )
    event_type = db.Column(
        db.String(64),
        nullable=False,
        unique=True,
        comment="事件类型标识，如 forbidden_parking、normal_parking 等"
    )
    points = db.Column(
        db.Integer,
        nullable=False,
        comment="该事件对应的加减分值，正数代表加分，负数代表扣分"
    )
    description = db.Column(
        db.String(255),
        comment="规则文字描述"
    )
    frequency_limit = db.Column(
        db.String(255),
        comment="频率与上限说明，比如“每次扣10，日累计上限-30”"
    )
    remark = db.Column(
        db.String(255),
        comment="备注，例如“超3次通报”"
    )
    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False,
        comment="创建时间"
    )
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        comment="更新时间"
    )

    def to_dict(self):
        """将规则对象转换为字典，用于JSON序列化"""
        return {
            'id': self.id,
            'event_type': self.event_type,
            'points': self.points,
            'description': self.description,
            'frequency_limit': self.frequency_limit,
            'remark': self.remark,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f"<ScoreRule {self.event_type} {self.points}>"

class ScoreLog(db.Model):
    """
    积分变动日志：记录每一次加分或扣分的明细。
    source 字段区分是系统自动、手动、上报审核还是申诉处理。
    """
    __tablename__ = 'score_logs'

    id = db.Column(
        db.BigInteger,
        primary_key=True,
        comment="日志主键，自增"
    )
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="关联的用户 ID"
    )
    vehicle_id = db.Column(
        db.Integer,
        db.ForeignKey('electric_vehicles.id', ondelete='SET NULL'),
        nullable=True,
        index=True,
        comment="关联的车辆 ID（可选），车辆删除后设为 NULL"
    )
    license_plate = db.Column(
        db.String(32),
        comment="当时的车牌号冗余存储"
    )
    event_type = db.Column(
        db.String(64),
        comment="触发的事件类型，对应 ScoreRule.event_type"
    )
    points = db.Column(
        db.Integer,
        nullable=False,
        comment="本次变动的分值"
    )
    source = db.Column(
        Enum('auto','manual','report','appeal', name='score_source'),
        nullable=False,
        comment="来源：auto 系统自动；manual 手动调整；report 上报审核；appeal 申诉处理"
    )
    timestamp = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False,
        comment="记录时间"
    )

    # ORM 关系，方便通过 log.user 或 log.vehicle 访问
    user = db.relationship('User', backref='score_logs')
    vehicle = db.relationship('ElectricVehicle', backref='score_logs')

    def __repr__(self):
        return f"<ScoreLog user={self.user_id} pts={self.points} src={self.source}>"

class ReportedEvent(db.Model):
    """
    上报事件表：师生在前端投诉/上报的违规事件，待管理员审核。
    审核后会生成一条 ScoreLog。
    """
    __tablename__ = 'reported_events'

    id = db.Column(
        db.BigInteger,
        primary_key=True,
        comment="上报记录主键"
    )
    reporter_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="上报人用户 ID"
    )
    vehicle_id = db.Column(
        db.Integer,
        db.ForeignKey('electric_vehicles.id', ondelete='SET NULL'),
        nullable=True,
        index=True,
        comment="相关车辆 ID，可选"
    )
    license_plate = db.Column(
        db.String(32),
        comment="相关车牌号"
    )
    event_type = db.Column(
        db.String(64),
        nullable=False,
        comment="上报的事件类型"
    )
    details = db.Column(
        db.Text,
        comment="上报详情，如图片地址或文字说明"
    )
    status = db.Column(
        Enum('pending','approved','rejected', name='report_status'),
        default='pending',
        nullable=False,
        comment="审核状态：pending 待审；approved 通过；rejected 驳回"
    )
    adjust_points = db.Column(
        db.Integer,
        default=0,
        nullable=False,
        comment="管理员审核时自定义的加减分值"
    )
    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False,
        comment="上报时间"
    )

    reporter = db.relationship('User', backref='reported_events')
    vehicle = db.relationship('ElectricVehicle', backref='reported_events')

    def __repr__(self):
        return f"<ReportedEvent id={self.id} status={self.status}>"

class Appeal(db.Model):
    """
    扣分申诉表：用户对系统扣分提出申诉，管理员审核后可撤销扣分（生成反向 ScoreLog）。
    """
    __tablename__ = 'appeals'

    id = db.Column(
        db.BigInteger,
        primary_key=True,
        comment="申诉主键"
    )

    # 添加关联到具体扣分记录的外键
    score_log_id = db.Column(
        db.BigInteger,
        db.ForeignKey('score_logs.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="申诉的扣分记录ID"
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="申诉用户 ID"
    )
    vehicle_id = db.Column(
        db.Integer,
        db.ForeignKey('electric_vehicles.id', ondelete='SET NULL'),
        nullable=True,
        index=True,
        comment="相关车辆 ID，可选"
    )
    license_plate = db.Column(
        db.String(32),
        comment="相关车牌号"
    )
    event_type = db.Column(
        db.String(64),
        nullable=False,
        comment="被申诉的事件类型"
    )
    reason = db.Column(
        db.Text,
        nullable=False,
        comment="申诉理由"
    )
    status = db.Column(
        Enum('pending','approved','rejected', name='appeal_status'),
        default='pending',
        nullable=False,
        comment="申诉状态：pending 待审；approved 同意；rejected 驳回"
    )
    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False,
        comment="申诉提交时间"
    )

    user = db.relationship('User', backref='appeals')
    vehicle = db.relationship('ElectricVehicle', backref='appeals')
     # 添加关系定义，方便通过 appeal.score_log 访问相关扣分记录
    score_log = db.relationship('ScoreLog', backref=db.backref('appeals', lazy=True))

    # 添加驳回原因字段
    rejection_reason = db.Column(
        db.String(255),
        nullable=True,
        comment="申诉驳回原因，仅在status='rejected'时有值"
    )

    def to_dict(self):
        """将申诉对象转换为字典，用于JSON序列化"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'score_log_id': self.score_log_id,
            'vehicle_id': self.vehicle_id,
            'license_plate': self.license_plate,
            'event_type': self.event_type,
            'reason': self.reason,
            'status': self.status,
            'rejection_reason': self.rejection_reason,  # 添加到dict方法中
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f"<Appeal id={self.id} status={self.status}>"


class Violation(db.Model):
    """
    违规记录表：系统自动或管理员录入的违规停车、逆行等事件，
    需在前端审核通过后记分并生成 ScoreLog。
    """
    __tablename__ = 'violations'

    id = db.Column(
        db.BigInteger,
        primary_key=True,
        comment="违规记录主键"
    )
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="违规用户 ID"
    )
    vehicle_id = db.Column(
        db.Integer,
        db.ForeignKey('electric_vehicles.id', ondelete='SET NULL'),
        nullable=True,
        index=True,
        comment="相关车辆 ID，可选"
    )
    license_plate = db.Column(
        db.String(32),
        comment="车牌号冗余"
    )
    event_type = db.Column(
        db.String(64),
        nullable=False,
        comment="事件类型，如 forbidden_parking、other_violation"
    )
    location = db.Column(
        db.String(128),
        comment="违规发生地点"
    )
    timestamp = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False,
        comment="违规发生时间"
    )
    status = db.Column(
        Enum('pending','approved','rejected', name='violation_status'),
        default='pending',
        nullable=False,
        comment="审核状态：pending 待审；approved 通过；rejected 驳回"
    )

    user = db.relationship('User', backref='violations')
    vehicle = db.relationship('ElectricVehicle', backref='violations')

    def to_dict(self):
        return {
          'id': self.id,
          'user_id': self.user_id,
          'vehicle_id': self.vehicle_id,
          'license_plate': self.license_plate,
          'event_type': self.event_type,
          'location': self.location,
          'timestamp': self.timestamp.isoformat(),
          'status': self.status
        }

    def __repr__(self):
        return f"<Violation {self.id} user={self.user_id} status={self.status}>"
