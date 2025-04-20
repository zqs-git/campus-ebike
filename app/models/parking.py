from datetime import datetime
from app import db
from app.models.vehicles import ElectricVehicle

class ParkingLot(db.Model):
    __tablename__ = 'parking_lots'

    # 主键
    id = db.Column(db.Integer, primary_key=True, comment="停车场ID")
    location_id = db.Column(db.Integer, db.ForeignKey('campus_locations.id'), nullable=False)  # 关联CampusLocation
    name = db.Column(db.String(50), nullable=False, comment="停车场名称")
    capacity = db.Column(db.Integer, nullable=False, comment="停车场总容量")
    occupied = db.Column(db.Integer, default=0, nullable=False, comment="已占用车位数")

    # 关联CampusLocation
    location = db.relationship('CampusLocation', backref='parking_lots', uselist=False)

    # 关联ParkingSpace
    parking_spaces = db.relationship('ParkingSpace', backref='parking_lot', lazy='dynamic')

    def __repr__(self):
        return f"<ParkingLot {self.name} at {self.location.name}>"

class ParkingSpace(db.Model):
    __tablename__ = 'parking_spaces'

    # 主键
    id = db.Column(db.Integer, primary_key=True, comment="停车位ID")
    parking_lot_id = db.Column(db.Integer, db.ForeignKey('parking_lots.id'), nullable=False)
    status = db.Column(db.String(10), default='available', nullable=False, comment="停车位状态")

    def __repr__(self):
        return f"<ParkingSpace {self.id} in Lot {self.parking_lot.name}>"

class ParkingRecord(db.Model):
    __tablename__ = 'parking_records'

    # 主键
    id = db.Column(db.Integer, primary_key=True, comment="停车记录ID")
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('electric_vehicles.id'), nullable=False)
    # 定义关系属性
    vehicle = db.relationship('ElectricVehicle', backref='parking_records')
    parking_space_id = db.Column(db.Integer, db.ForeignKey('parking_spaces.id'), nullable=False)
    park_in_time = db.Column(db.DateTime, default=datetime.utcnow, comment="停车时间")
    park_out_time = db.Column(db.DateTime, nullable=True, comment="出库时间")

    # 关联停车位
    parking_space = db.relationship('ParkingSpace')

    def __repr__(self):
        return f"<ParkingRecord {self.id} for Vehicle {self.vehicle_id}>"
