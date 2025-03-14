# tests/test_models/test_user.py

from app.models.users import User
def test_user_creation(test_app, test_db, new_user):
    """测试用户创建流程"""
    with test_app.app_context():
        # 设置密码并验证哈希生成
        new_user.password = 'Init@123'
        
        # 添加到数据库
        test_db.session.add(new_user)
        test_db.session.commit()
        
        # 验证数据库记录
        user_in_db = User.query.first()
        assert user_in_db.school_id == '202301001'
        assert user_in_db.phone == '13800138000'
        assert user_in_db.password_hash is not None

def test_password_verification(test_app, new_user):
    """测试密码验证逻辑"""
    with test_app.app_context():
        # 正确密码验证
        new_user.password = 'SecurePass123!'
        assert new_user.verify_password('SecurePass123!') is True
        
        # 错误密码验证
        assert new_user.verify_password('WrongPass456@') is False
        
        # 空密码用户验证（模拟微信用户）
        new_user.password_hash = None
        assert new_user.verify_password('any_password') is False