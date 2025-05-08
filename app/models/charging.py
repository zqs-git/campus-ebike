from app import db
from datetime import datetime
import enum
# ---------------------
# 枚举定义
# ---------------------
class ChargingPileStatus(enum.Enum):
    available = "available"   # 空闲
    reserved  = "reserved"    # 已预约
    charging  = "charging"    # 正在充电
    finished  = "finished"    # 充电完成
    offline   = "offline"     # 离线

class ChargingSessionStatus(enum.Enum):
    reserved  = "reserved"   # 已预约，待开始
    ongoing   = "ongoing"    # 正在充电
    completed = "completed"  # 已完成
    cancelled = "cancelled"  # 已取消

# ---------------------
# 充电桩模型
# ---------------------
class ChargingPile(db.Model):
    __tablename__ = 'charging_piles'
    __table_args__ = (
        db.UniqueConstraint('location_id', 'name', name='uix_location_pile_name'),
    )

    id          = db.Column(db.Integer, primary_key=True, autoincrement=True)
    location_id = db.Column(
        db.Integer,
        db.ForeignKey('campus_locations.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    name        = db.Column(db.String(50), nullable=False)
    connector   = db.Column(db.String(20), nullable=False)
    power_kw    = db.Column(db.Float, nullable=False)
    fee_rate    = db.Column(db.Float, nullable=False)
    status      = db.Column(
        db.Enum(ChargingPileStatus),
        default=ChargingPileStatus.available,
        nullable=False,
        index=True
    )
    updated_at  = db.Column(
        db.DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # 关系
    location    = db.relationship('CampusLocation', backref=db.backref('charging_piles', cascade='all, delete-orphan'))
    sessions    = db.relationship(
        'ChargingSession',
        back_populates='pile',
        cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f"<ChargingPile id={self.id}, name={self.name}, status={self.status.value}>"

# ---------------------
# 充电会话模型
# ---------------------
class ChargingSession(db.Model):
    __tablename__ = 'charging_sessions'
    __table_args__ = (
        db.UniqueConstraint('pile_id', 'slot_time', name='uix_pile_slot'),
        db.Index('ix_session_user', 'user_id'),
        db.Index('ix_session_status', 'status'),
    )

    id          = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id     = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False
    )
    pile_id     = db.Column(
        db.Integer,
        db.ForeignKey('charging_piles.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    vehicle_id  = db.Column(
        db.Integer,
        db.ForeignKey('electric_vehicles.id', ondelete='CASCADE'),
        nullable=False
    )

    # 预约时段和创建时间
    slot_time   = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        index=True
    )
    created_at  = db.Column(
        db.DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
        index=True
    )

    # 开始/结束
    start_time  = db.Column(db.DateTime(timezone=True), nullable=True)
    end_time    = db.Column(db.DateTime(timezone=True), nullable=True)

    status      = db.Column(
        db.Enum(ChargingSessionStatus),
        default=ChargingSessionStatus.reserved,
        nullable=False
    )
    energy_kwh  = db.Column(db.Float, nullable=True)
    fee_amount  = db.Column(db.Float, nullable=True)

    reserved_date       = db.Column(db.Date, nullable=True)
    reserved_start_time = db.Column(db.Time, nullable=True)
    reserved_end_time   = db.Column(db.Time, nullable=True)


    # 关系
    pile        = db.relationship('ChargingPile', back_populates='sessions')
    user        = db.relationship('User', backref=db.backref('charging_sessions', cascade='all, delete-orphan'))
    vehicle     = db.relationship('ElectricVehicle', back_populates='sessions')

    def __repr__(self):
        return (
            f"<ChargingSession id={self.id}, user={self.user_id}, "
            f"pile={self.pile_id}, slot={self.slot_time.isoformat()}, status={self.status.value}>"
        )
