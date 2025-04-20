# app/models/user.py
from app import db
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import CheckConstraint, Index

class User(db.Model):
    """
    用户核心数据模型
    处理校园用户与访客的认证、权限及关联关系
    """
    __tablename__ = 'users'
    __table_args__ = (
        # 角色枚举约束（数据库层面校验）
        CheckConstraint(
            "role IN ('student','staff','admin','visitor')", 
            name='check_user_role'
        ),
        # 复合唯一约束：确保至少一种登录方式且不重复（PostgreSQL语法）
        Index('idx_unique_login', 
              'school_id', 
              'phone', 
              'wechat_openid', 
              unique=True,
              postgresql_where=db.or_(
                  db.text("school_id IS NOT NULL"),
                  db.text("phone IS NOT NULL"),
                  db.text("wechat_openid IS NOT NULL")
              ))
    )

    # 主键
    id = db.Column(db.Integer, primary_key=True, comment="自增主键")
    
    # 身份识别字段
    school_id = db.Column(
        db.String(20), 
        unique=True, 
        nullable=True, 
        comment="学工号（校内人员必填）"
    )
    phone = db.Column(
        db.String(11), 
        unique=True, 
        nullable=True, 
        comment="手机号（带唯一约束）"
    )
    wechat_openid = db.Column(
        db.String(128), 
        unique=True, 
        nullable=True, 
        comment="微信开放平台唯一标识"
    )
    
    # 安全相关字段
    password_hash = db.Column(
        db.String(255), 
        nullable=True, 
        comment="密码哈希（可为空，支持无密码登录）"
    )
    
    # 权限控制字段
    role = db.Column(
        db.String(10), 
        default='student', 
        nullable=False,
        comment="用户角色：student(学生)/staff(教职工)/admin(管理员)/visitor(访客)"
    )
    is_active = db.Column(
        db.Boolean, 
        default=True, 
        comment="账户状态（False表示禁用）"
    )
    
    # 时间戳字段
    created_at = db.Column(
        db.DateTime, 
        default=datetime.utcnow, 
        comment="用户创建时间（UTC时区）"
    )

    # 新增字段
    name = db.Column(db.String(50))  # 姓名
    id_card = db.Column(db.String(18), unique=True, nullable=True)  # 身份证号
    
    # license_plate = db.Column(db.String(15))  # 车牌号
    # permission_expire = db.Column(db.DateTime, nullable=True)  # 权限有效期（访客专用）

    last_login = db.Column(db.DateTime, nullable=True)  # ✅ 允许空值


    # 关联电动车（用户拥有多辆车）
    vehicles = db.relationship(
        'ElectricVehicle', 
        backref='owner', 
        lazy='dynamic'
    )

    # 关联访客通行证（用户拥有一个通行证）
    visitor_pass = db.relationship(
        'VisitorPass',
        backref='user',
        uselist=False,
        cascade="all, delete"
    )

    def update_login_time(self):
        try:
            self.last_login = datetime.utcnow()
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"更新登录时间失败: {e}")


    @property
    def license_plate(self):
        """根据角色返回对应的车牌号"""
        if self.role == 'visitor':
            return self.visitor_pass.license_plate if self.visitor_pass else None
        else:
            # 学生/教职工通过关联车辆获取车牌号
            return self.vehicles.first().plate_number if self.vehicles.first() else None
        
    @license_plate.setter
    def license_plate(self, plate):
        """仅允许访客设置车牌号"""
        if self.role != 'visitor':
            raise ValueError("非访客用户不能直接设置车牌号！")
        # 创建或更新访客通行证
        if not self.visitor_pass:
            self.visitor_pass = VisitorPass(license_plate=plate,expires_at=datetime.utcnow() + timedelta(days=7))
        else:
            self.visitor_pass.license_plate = plate
            self.visitor_pass.expires_at = datetime.utcnow() + timedelta(days=7)  # 设置默认有效期

    def is_visitor_pass_valid(self):
        """检查访客通行证是否仍然有效"""
        if self.role != 'visitor' or not self.visitor_pass:
            return False  # 不是访客，或者没有通行证 -> 无效
        return datetime.utcnow() < self.visitor_pass.expires_at  # 过期时间未到 -> 有效


    # region 密码安全方法
    @property
    def password(self):
        """防止直接读取密码明文"""
        raise AttributeError('密码字段不可读')

    @password.setter
    def password(self, password):
        """自动生成安全哈希"""
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        """验证密码有效性（处理空密码场景）"""
        if not self.password_hash:
            return False  # 无密码用户直接返回验证失败
        return check_password_hash(self.password_hash, password)
    # endregion

    def __repr__(self):
        """调试表示方法"""
        return f'<User {self.school_id or self.phone}>'
    


#访客通行证模型
class VisitorPass(db.Model):
    __tablename__ = 'visitor_passes'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    license_plate = db.Column(db.String(15), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)  # 临时通行证有效期
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<VisitorPass {self.license_plate} expires at {self.expires_at}>"