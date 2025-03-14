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

@pytest.fixture(scope='session')
def test_db(test_app):
    with test_app.app_context():
        # ✅ 应用所有迁移
        from flask_migrate import upgrade
        upgrade()  # 代替 db.create_all()
        yield db
        # 无需手动清理，内存数据库自动销毁

@pytest.fixture
def client(test_app):
    """提供测试客户端（每次测试独立）"""
    return test_app.test_client()

@pytest.fixture
def new_user():
    """生成标准测试用户（函数级作用域）"""
    return User(
        school_id='202301001',
        phone='13800138000',
        role='student',
        # ✅ 必须设置密码（根据模型要求）
        password='TestPass123!'  
    )