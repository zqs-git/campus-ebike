from flask import Blueprint, jsonify  # 导入Blueprint和jsonify
from .models.users import User  # 从models文件导入User模型
from .extensions import db  # 从extensions文件导入db（SQLAlchemy）

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return "Flask 配置成功！"

# 创建一个Blueprint对象，用于注册路由
test_bp = Blueprint('test', __name__)

# 定义一个路由和视图函数，用于创建一个测试用户
@test_bp.route('/create-test-user')
def create_test_user():
    """创建一个测试用户并保存到数据库"""
    
    # 创建一个新的用户对象，密码未加密（实际项目中应使用加密）
    new_user = User(
        username='testuser',  # 用户名
        email='test@example.com',  # 用户邮箱
        password='secure_password'  # 用户密码，实际项目应使用加密函数处理密码
    )
    
    # 将新用户添加到数据库会话
    db.session.add(new_user)
    
    # 提交会话，保存数据到数据库
    db.session.commit()
    
    # 返回一个JSON响应，包含成功信息和新用户的ID
    return jsonify({"msg": "测试用户已创建", "id": new_user.id})