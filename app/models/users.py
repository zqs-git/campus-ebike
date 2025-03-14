# app/models/user.py
from app import db
from datetime import datetime
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
        db.String(128), 
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
    id_card = db.Column(db.String(18), unique=True)  # 身份证号
    license_plate = db.Column(db.String(15))  # 车牌号
    permission_expire = db.Column(db.DateTime)  # 权限有效期（访客专用）

    last_login = db.Column(db.DateTime)  # 新增最后登录时间字段
    
    # 关联关系（一对多）
    # vehicles = db.relationship(
    #     'Vehicle', 
    #     backref='owner', 
    #     lazy='dynamic',
    # )

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