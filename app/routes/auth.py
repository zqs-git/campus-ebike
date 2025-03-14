# app/routes/auth.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from app.models.users import User
from app import db

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    多角色用户注册接口
    支持校内人员（student/staff）和校外访客（visitor）注册
    请求体示例:
    {
        "user_type": "internal",  # 用户类型 internal-校内人员/external-校外访客
        "school_id": "20231001",  # 学工号（校内必填）
        "id_card": "11010119900307783X",  # 身份证号（校外必填）
        "name": "张三",
        "password": "Abc12345",
        "phone": "13800138000",
        "license_plate": "京A12345"  # 车牌号（校外必填）
    }
    """
    data = request.get_json()
    user_type = data.get('user_type')

    # --------------------------
    # 基础参数校验
    # --------------------------
    if user_type not in ['internal', 'external']:
        return jsonify({"code":400, "msg":"无效的用户类型"}),400

    if not data.get('password') or len(data['password'])<6:
        return jsonify({"code":400, "msg":"密码需6位以上"}),400

    # --------------------------
    # 分类型校验
    # --------------------------
    if user_type == 'internal':
        # 校内人员校验
        if not data.get('school_id'):
            return jsonify({"code":400, "msg":"学工号不能为空"}),400
            
        # 模拟调用教务系统API验证学工号有效性
        if not validate_school_info(data['school_id'], data.get('name')):
            return jsonify({"code":403, "msg":"学工号验证失败"}),403

        # 检查学工号重复
        if User.query.filter_by(school_id=data['school_id']).first():
            return jsonify({"code":409, "msg":"该学工号已注册"}),409

    else:
        # 校外访客校验
        if not data.get('id_card') or not data.get('license_plate'):
            return jsonify({"code":400, "msg":"身份证号和车牌号不能为空"}),400

        # 模拟公安系统身份核验
        if not validate_id_card(data['id_card']):
            return jsonify({"code":403, "msg":"身份证号不合法"}),403

        # 检查车牌是否已被绑定
        if User.query.filter_by(license_plate=data['license_plate']).first():
            return jsonify({"code":409, "msg":"该车牌号已存在"}),409

    try:
        # --------------------------
        # 用户对象创建
        # --------------------------
        new_user = User(
            school_id=data.get('school_id'),
            password=data['password'],  # 自动加密
            phone=data.get('phone'),
            name=data.get('name'),
            license_plate=data.get('license_plate'),
            id_card=data.get('id_card'),
            role='visitor' if user_type=='external' else 'student'  # 角色分配
        )

        # 设置访客有效期
        if user_type == 'external':
            new_user.permission_expire = datetime.utcnow() + timedelta(hours=24)

        db.session.add(new_user)
        db.session.commit()

        return jsonify({
            "code":201,
            "msg":"注册成功",
            "data":{
                "user_id": new_user.id,
                "role": new_user.role,
                "expire_time": new_user.permission_expire.isoformat() if user_type=='external' else None
            }
        }),201

    except Exception as e:
        db.session.rollback()
        return jsonify({"code":500, "msg":"服务器错误"}),500

# --------------------------
# 模拟验证服务
# --------------------------
def validate_school_info(school_id, name):
    """模拟教务系统验证（需替换为实际API调用）"""
    # 实际应调用教务系统接口验证学工号与姓名匹配性
    return True if school_id.startswith('20') else False

def validate_id_card(id_number):
    """模拟公安系统验证（需替换为实际API调用）"""
    # 实际应调用公安系统接口验证身份证合法性
    return len(id_number) == 18


# @auth_bp.route('/login', methods=['POST'])
# def login():
#     """
#     用户登录接口
#     请求示例：
#     {
#         "username": "13800138000",  # 支持手机号或学工号
#         "password": "TestPass123!"
#     }
#     响应示例：
#     {
#         "code": 200,
#         "msg": "登录成功",
#         "data": {
#             "access_token": "xxx",
#             "refresh_token": "xxx",
#             "user_info": {
#                 "user_id": 1,
#                 "role": "student",
#                 "name": "张三"
#             }
#         }
#     }
#     """

#     # 获取请求数据（JSON格式）
#     data = request.get_json()

#     # 基础校验：确保请求数据存在，并包含 "username" 和 "password" 字段
#     if not data or 'username' not in data or 'password' not in data:
#         return jsonify({"code": 400, "msg": "缺少用户名或密码"}), 400

#     # 去除用户名前后空格，提取密码
#     username = data['username'].strip()
#     password = data['password']

#     # 查找用户（支持手机号或学工号登录）
#     user = User.query.filter(
#         (User.phone == username) | (User.school_id == username)
#     ).first()

#     # 如果用户不存在，或密码错误，则返回 401 未授权
#     if not user or not user.verify_password(password):
#         return jsonify({"code": 401, "msg": "用户名或密码错误"}), 401

#     # 生成访问令牌（access_token）和刷新令牌（refresh_token）
#     # identity=user，意味着 JWT 令牌中的 "sub" 字段会存储用户的身份信息
#     access_token = create_access_token(identity=user)
#     refresh_token = create_refresh_token(identity=user)

#     # 更新用户的最后登录时间
#     user.last_login = datetime.utcnow()
#     db.session.commit()

#     # 返回 JSON 响应，包含 access_token、refresh_token 和用户基本信息
#     return jsonify({
#         "code": 200,
#         "msg": "登录成功",
#         "data": {
#             "access_token": access_token,  # 访问令牌（用于验证用户身份）
#             "refresh_token": refresh_token,  # 刷新令牌（用于获取新的访问令牌）
#             "user_info": {
#                 "user_id": user.id,  # 用户 ID
#                 "role": user.role,  # 用户角色（例如：student, admin）
#                 "name": user.name  # 用户姓名
#             }
#         }
#     }), 200


# from flask import jsonify
# from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token

# @auth_bp.route('/refresh', methods=['POST'])
# @jwt_required(refresh=True)  # ✅ 需要携带有效的 Refresh Token
# def refresh_token():
    """
    令牌刷新接口
    - 客户端在 Access Token 过期后，可以使用 Refresh Token 重新获取新的 Access Token。
    - 请求示例：
      POST /api/auth/refresh
      Headers: {"Authorization": "Bearer <refresh_token>"}
    - 响应示例：
      {
          "code": 200,
          "msg": "令牌刷新成功",
          "data": {
              "access_token": "新的访问令牌"
          }
      }
    """

    # ✅ 获取当前用户身份（从 Refresh Token 中解析出的用户信息）
    current_user = get_jwt_identity()

    # ✅ 生成新的 Access Token
    new_token = create_access_token(identity=current_user)

    # ✅ 返回新的 Access Token
    return jsonify({
        "code": 200,
        "msg": "令牌刷新成功",
        "data": {
            "access_token": new_token  # 返回新的 Access Token
        }
    }), 200




# # ✅ 登出接口（令牌拉黑）
# @auth_bp.route('/logout', methods=['DELETE'])
# @jwt_required()  # 需要携带有效的 JWT 访问
# def logout():
#     """
#     用户登出接口：
#     - 该接口会将当前用户的 JWT 加入黑名单，使其失效，防止继续使用该令牌访问系统。
#     - 请求示例：
#       DELETE /api/auth/logout
#       Headers: {"Authorization": "Bearer <access_token>"}
#     - 响应示例：
#       {
#           "code": 200,
#           "msg": "成功登出"
#       }
#     """

#     # ✅ 获取当前令牌的 jti（JWT 唯一标识符）
#     jti = get_jwt()["jti"]

#     # ✅ 将该令牌存入 Redis 黑名单，并设置过期时间（与 JWT 过期时间一致）
#     jwt_redis_blocklist.set(jti, "", ex=timedelta(hours=1))  # 1小时后自动删除

#     # ✅ 返回成功登出响应
#     return jsonify({"code": 200, "msg": "成功登出"}), 200
