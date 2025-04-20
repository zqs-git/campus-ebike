from app import db
from datetime import datetime

class CampusLocation(db.Model):
    __tablename__ = 'campus_locations'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)  # 地点名称（如“犀浦校区图书馆”）
    latitude = db.Column(db.Float, nullable=False)  # 纬度坐标（GCJ-02坐标系）
    longitude = db.Column(db.Float, nullable=False)  # 经度坐标（GCJ-02坐标系）
    location_type = db.Column(
        db.String(20),
        nullable=False,
        default='other',
        comment="类型：parking（停车场）、charging（充电桩）、building（教学楼）、dining（食堂）等"
    )
    description = db.Column(db.String(200), nullable=True)  # 地点描述
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 创建时间
    
    # 新增字段：存储区域的路径数据（多边形的顶点坐标）
    path = db.Column(db.JSON, nullable=False, comment="区域路径（多边形顶点坐标）")
    
    def __repr__(self):
        return f'<CampusLocation {self.name}>'
