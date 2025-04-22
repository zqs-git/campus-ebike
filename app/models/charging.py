from app import db
from datetime import datetime
import enum

# 充电桩状态
class ChargingPileStatus(enum.Enum):
    available = "available"  # 空闲
    reserved = "reserved"    # 已预约
    charging = "charging"    # 正在充电
    finished = "finished"    # 充电完成
    offline = "offline"      # 离线

# 充电会话状态
class ChargingSessionStatus(enum.Enum):
    reserved = "reserved"  # 已预约，待开始
    ongoing = "ongoing"    # 正在充电
    completed = "completed" # 已完成
    cancelled = "cancelled" # 取消

# 充电桩表
class ChargingPile(db.Model):
    __tablename__ = 'charging_piles'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    location_id = db.Column(db.Integer, db.ForeignKey('campus_locations.id'), nullable=False)  # 外键，关联地点表
    name = db.Column(db.String(50), nullable=False)  # 充电桩名称
    connector = db.Column(db.String(20), nullable=False)  # 充电接口类型（例如 "Type2"）
    power_kw = db.Column(db.Float, nullable=False)  # 额定功率（单位：kW）
    fee_rate = db.Column(db.Float, nullable=False)  # 每度电的费用（单位：元）
    status = db.Column(db.Enum(ChargingPileStatus), default=ChargingPileStatus.available, nullable=False)  # 当前状态
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 更新时间
    
    # 充电桩与地点的关系
    location = db.relationship('CampusLocation', backref='charging_piles')

    # 充电桩与充电会话的关系
    sessions = db.relationship('ChargingSession', back_populates='pile', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<ChargingPile {self.name}, Location: {self.location.name}>"

# 充电会话表
class ChargingSession(db.Model):
    __tablename__ = 'charging_sessions'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # 用户ID
    pile_id = db.Column(db.Integer, db.ForeignKey('charging_piles.id'), nullable=False)  # 充电桩ID
    start_time = db.Column(db.DateTime, nullable=True)  # 开始时间
    end_time = db.Column(db.DateTime, nullable=True)  # 结束时间
    status = db.Column(db.Enum(ChargingSessionStatus), default=ChargingSessionStatus.reserved, nullable=False)  # 充电会话状态
    energy_kwh = db.Column(db.Float, nullable=True)  # 充电量（单位：kWh）
    fee_amount = db.Column(db.Float, nullable=True)  # 费用（单位：元）

    # 充电会话与充电桩的关系
    pile = db.relationship('ChargingPile', back_populates='sessions')
    
    # 充电会话与用户的关系
    user = db.relationship('User')

    def __repr__(self):
        return f"<ChargingSession {self.id}, User: {self.user_id}, Pile: {self.pile_id}>"
