from app import db
from datetime import datetime

class ElectricVehicle(db.Model):
    """
    电动车模型
    """
    __tablename__ = 'electric_vehicles'

    # 主键
    id = db.Column(db.Integer, primary_key=True, comment="电动车ID")

    # 绑定用户（外键关联 User 表）
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, comment="车辆所有者ID")

    # 车辆基本信息
    brand = db.Column(db.String(50), nullable=False, comment="车辆品牌")
    model = db.Column(db.String(50), nullable=False, comment="车辆型号")
    color = db.Column(db.String(20), nullable=True, comment="车辆颜色")
    
    # 车牌号，唯一约束
    plate_number = db.Column(db.String(15), unique=True, nullable=False, comment="车牌号")

    # 电池容量（单位：Wh）
    battery_capacity = db.Column(db.Integer, nullable=True, comment="电池容量（单位：Wh）")

    # 注册时间
    registered_at = db.Column(db.DateTime, default=datetime.utcnow, comment="注册时间")

    # 车辆状态（active=使用中, inactive=停用）
    status = db.Column(db.String(10), default='active', nullable=False, comment="车辆状态")

    def __repr__(self):
        return f"<ElectricVehicle {self.plate_number} owned by {self.owner_id}>"