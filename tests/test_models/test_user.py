# # tests/test_models/test_user.py

from app.models.users import User
# def test_user_creation(test_app, test_db, new_user):
#     """测试用户创建流程"""
#     with test_app.app_context():
#         # 设置密码并验证哈希生成
#         new_user.password = 'Init@123'
        
#         # 添加到数据库
#         test_db.session.add(new_user)
#         test_db.session.commit()
        
#         # 验证数据库记录
#         user_in_db = User.query.first()
#         assert user_in_db.school_id == '202301001'
#         assert user_in_db.phone == '13800138000'
#         assert user_in_db.password_hash is not None

# def test_password_verification(test_app, new_user):
#     """测试密码验证逻辑"""
#     with test_app.app_context():
#         # 正确密码验证
#         new_user.password = 'SecurePass123!'
#         assert new_user.verify_password('SecurePass123!') is True
        
#         # 错误密码验证
#         assert new_user.verify_password('WrongPass456@') is False
        
#         # 空密码用户验证（模拟微信用户）
#         new_user.password_hash = None
#         assert new_user.verify_password('any_password') is False


import json
from datetime import datetime
from flask_jwt_extended import create_access_token, jwt_required
from app.extensions import jwt  # 关键导入

def test_successful_login(client, test_user):
    """测试正常登录流程"""
    response = client.post('/api/auth/login', json={
        "username": test_user.phone,
        "password": "TestPass123!"
    },headers={"Content-Type": "application/json"})
    assert response.status_code == 200
    assert 'access_token' in response.json['data']

def test_inactive_user(client, inactive_user):
    """测试禁用账户登录"""
    response = client.post('/api/auth/login', json={
        "username": inactive_user.phone,
        "password": "TestPass123!"
    },headers={"Content-Type": "application/json"})
    assert response.status_code == 403
    assert "账户已被禁用" in response.json['msg']

def test_logout(client, test_db, test_user):
    """确保 test_user 已经存入数据库"""
    user = User.query.filter_by(id=test_user.id).first()
    assert user is not None  # 确保用户存在

    # 生成有效令牌
    access_token = create_access_token(identity=str(test_user.id))
    print(f"🟢 生成的 access_token: {access_token}")  # ✅ 观察令牌是否正确

    # 带令牌请求登出
    response = client.delete(
        '/api/auth/logout',
        headers={'Authorization': f'Bearer {access_token}'}
    )

    print(f"🔴 登出返回的状态码: {response.status_code}")
    print(f"🔴 登出返回的内容: {response.json}")

    assert response.status_code == 200
