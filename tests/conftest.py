import pytest
from app import create_app, db
from app.models.users import User

@pytest.fixture(scope='module')
def test_app():
    """创建测试专用的Flask应用实例"""
    # ✅ 指定使用测试配置
    app = create_app(config_name='testing')
    
    # 激活应用上下文（用于数据库操作）
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture(scope="module")
def test_db(test_app):
    with test_app.app_context():
        from flask_migrate import upgrade
        upgrade()
        yield db
        db.session.rollback()  # 🔹 避免事务未提交的问题
        db.session.remove()  # 🔹 确保 session 关闭


@pytest.fixture
def client(test_app):
    """提供测试客户端（每次测试独立）"""
    return test_app.test_client()

# @pytest.fixture
# def new_user():
#     """生成标准测试用户（函数级作用域）"""
#     return User(
#         school_id='202301001',
#         phone='13800138000',
#         role='student',
#         # ✅ 必须设置密码（根据模型要求）
#         password='TestPass123!'  
#     )

import random

@pytest.fixture
def test_user(test_db):
    """创建或获取测试用户，避免重复插入"""
    unique_school_id = f"2023{random.randint(10000, 99999)}"  # 🔹 生成唯一的 school_id
    unique_phone = f"13800{random.randint(10000, 99999)}"  # 生成唯一手机号
    
    user = User.query.filter_by(phone=unique_phone).first()

    if not user:
        user = User(
            school_id=unique_school_id,  # ✅ 生成唯一 school_id
            phone=unique_phone,
            role="student"
        )
        user.password = "TestPass123!"
        test_db.session.add(user)
        test_db.session.commit()

    return user



# @pytest.fixture
# def inactive_user():
#     """Create an inactive test user."""
#     user = User(name="inactiveuser",is_active=False)
#     user.password = "inactivepassword"
#     db.session.add(user)
#     db.session.commit()
#     return user

@pytest.fixture
def inactive_user(test_db):
    """创建或获取禁用用户，避免重复插入"""
    unique_phone = f"13800{random.randint(10000, 99999)}"  # 生成唯一手机号
    user = User.query.filter_by(phone=unique_phone).first()

    if not user:
        user = User(
            school_id="202310004",
            phone=unique_phone,
            role="student",
            is_active=False
        )
        user.password = "InactivePass123!"
        test_db.session.add(user)
        test_db.session.commit()

    return user
