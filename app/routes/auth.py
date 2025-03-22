# app/routes/auth.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token,get_jwt,jwt_required,current_user
from flask_jwt_extended import JWTManager, get_jwt_identity
from werkzeug.security import generate_password_hash
from app.models.users import User,VisitorPass
from app.models.vehicles import ElectricVehicle
from app import db
from sqlalchemy.exc import IntegrityError, OperationalError
from datetime import datetime, timedelta
import logging

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    多角色用户注册接口
    支持校内人员（student/staff）和校外访客（visitor）注册
    请求体示例:
    {
        "role": "student",  # 用户角色
        "school_id": "20231001",  # 学工号（校内必填）
        "id_card": "11010119900307783X",  # 身份证号（校外必填）
        "name": "张三",
        "password": "Abc12345",
        "phone": "13800138000",
        "license_plate": "京A12345"  # 车牌号（校外必填）
    }
    """
    data = request.get_json()
    print(f"Received registration data: {data}")  # ✅ 添加调试日志
    if not data:
        return jsonify({"msg": "没有收到数据"}), 400
    
    role = data.get('role')
    print(f"Received role: {role}")  # ✅ 添加调试日志
    license_plate = data.get('license_plate', None)  # ✅ 添加车牌号字段
    print(f"Received license plate: {license_plate}")  # ✅ 添加调试日志


    # --------------------------
    # 基础参数校验
    # --------------------------
    if role not in ['student', 'staff', 'admin', 'visitor']:
        return jsonify({"code": 400, "msg": "无效的角色"}), 400

    if not data.get('password') or len(data['password']) < 6:
        return jsonify({"code": 400, "msg": "密码需6位以上"}), 400

    # --------------------------
    # 分类型校验
    # --------------------------
    if role in ['student', 'staff']:
        # 校内人员校验
        if not data.get('school_id'):
            return jsonify({"code": 400, "msg": "学工号不能为空"}), 400
            
        # 模拟调用教务系统API验证学工号有效性
        if not validate_school_info(data['school_id'], data.get('name')):
            return jsonify({"code": 403, "msg": "学工号验证失败"}), 403

        # 检查学工号重复
        if User.query.filter_by(school_id=data['school_id']).first():
            return jsonify({"code": 409, "msg": "该学工号已注册"}), 409

    if role == 'visitor':
        # 校外访客校验
        if not data.get('id_card') or not data.get('license_plate'):
            return jsonify({"code": 400, "msg": "身份证号和车牌号不能为空"}), 400
        
        print(f"Validating ID card: {data['id_card']}")  # ✅ 添加调试日志
        print(f"Validating license plate: {data['license_plate']}")  # ✅ 添加调试日志

        # # 模拟公安系统身份核验
        # if not validate_id_card(data['id_card']):
        #     return jsonify({"code": 403, "msg": "身份证号不合法"}), 403

        # # 检查车牌是否已被绑定
        # if User.query.filter_by(license_plate=data['license_plate']).first():
        #     return jsonify({"code": 409, "msg": "该车牌号已存在"}), 409

    try:
        # --------------------------
        # 用户对象创建
        # --------------------------
        new_user = User(
            school_id=data.get('school_id') if role in ['student', 'staff'] else None,  # 校内人员插入 school_id
            password=data['password'],  # 自动加密
            phone=data.get('phone'),
            name=data.get('name'),
            # license_plate=data.get('license_plate'),
            id_card=data.get('id_card') or None,
            role=role
        )
        # 访客需要设置临时通行证
        if role == 'visitor':
            if not license_plate:
                return jsonify({"code": 400, "msg": "访客必须提供车牌号"}), 400
            # 设置车牌号会自动创建 VisitorPass 记录
            new_user.license_plate = license_plate

        print(f"New user object: {new_user}")  # ✅ 添加调试日志

        # # 设置访客有效期
        # if role == 'visitor':
        #     new_user.permission_expire = datetime.utcnow() + timedelta(hours=24)

        db.session.add(new_user)
        db.session.commit()

        return jsonify({
            "code": 201,
            "msg": "注册成功",
            "data": {
                "user_id": new_user.id,
                "role": new_user.role,
                # "expire_time": new_user.permission_expire.isoformat() if role == 'visitor' else None
            }
        }), 201

    except IntegrityError as e:
        db.session.rollback()
        print(f"IntegrityError: {e}")  # ✅ 打印数据库约束错误
        return jsonify({'error': 'IntegrityError', 'details': str(e)}), 400

    except OperationalError as e:
        db.session.rollback()
        print(f"OperationalError: {e}")  # ✅ 打印数据库操作错误
        return jsonify({'error': 'OperationalError', 'details': str(e)}), 500

    except Exception as e:
        db.session.rollback()
        print(f"Unknown Error: {e}")  # ✅ 打印未知错误
        return jsonify({'error': 'Registration failed', 'details': str(e)}), 500


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


# 配置日志
logging.basicConfig(level=logging.INFO)

@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录接口"""
    data = request.get_json()

    # **修正：确保 data 是字典**
    if not isinstance(data, dict):
        return jsonify({"code": 400, "msg": "请求数据格式错误"}), 400

    # **修正：避免 NoneType 错误**
    username = (data.get("username") or "").strip().lower()
    password = data.get("password") or ""

    # **校验字段是否为空**
    if not username or not password:
        return jsonify({"code": 400, "msg": "请求必须包含用户名和密码"}), 400

    logging.info(f"查询用户名: {username}")
    # 查询用户
    user = User.query.filter(
        (User.phone == username) | 
        (User.school_id == username)
    ).first()

    if not user:
        logging.warning("❌ 用户不存在")
        return jsonify({"code": 401, "msg": "用户名或密码错误"}), 401

    logging.info(f"找到用户: ID={user.id}, is_active={user.is_active}")

    if not user.is_active:
        logging.warning("❌ 账户被禁用")
        return jsonify({"code": 403, "msg": "账户已被禁用"}), 403

    logging.info(f"输入密码: {password}")
    logging.info(f"数据库存储哈希: {user.password_hash}")
    logging.info(f"密码校验结果: {user.verify_password(password)}")

    if not user.verify_password(password):
        logging.warning("❌ 密码错误")
        return jsonify({"code": 401, "msg": "用户名或密码错误"}), 401

    logging.info("✅ 密码正确，生成 JWT")

    # 访客通行证过期处理
    if user.role == 'visitor' and not user.is_visitor_pass_valid():
        # 如果通行证过期，返回需要更新的信息（车牌号等）
        logging.warning(f"❌ 用户 {user.id} 的访客通行证已过期，无法登录")
        db.session.rollback()  # 回滚事务
        return jsonify({
            "code": 403,
            "msg": "您的通行证已过期，请更新通行证",
            "need_update": True,
            "user_info": {
                "license_plate": user.license_plate or ''
            }
        }), 403

    # 生成 JWT 令牌
    # user = User.query.filter_by(username=form.username.data).first()
    access_token = create_access_token(identity=str(user.id),additional_claims={"role": user.role} )  # ✅ 确保是字符串, 添加角色到 JWT claims
    refresh_token = create_refresh_token(identity=str(user.id))  # ✅ 确保是字符串

    # 直接在查询后更新登录时间，不需要显式调用 db.session.commit() 之前
    user.last_login = datetime.now()

    try:
        db.session.commit()  # 提交数据库更改
        logging.info("✅ 登录时间已成功更新")
    except Exception as e:
        db.session.rollback()  # 如果发生异常，回滚事务
        logging.error(f"❌ 数据库事务回滚，错误信息: {e}")
        return jsonify({"code": 500, "msg": "数据库操作失败，请稍后再试"}), 500

    return jsonify({
        "code": 200,
        "msg": "登录成功",
        "data": {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user_info": {
                "user_id": user.id,
                "role": user.role,
                "name": user.name
            }
        }
    }), 200

@auth_bp.route("/updateVisitorPass", methods=["POST"])
def update_visitor_pass():
    # 获取请求中的数据
    data = request.json
    print(f"Received data: {data}")  # ✅ 添加调试日志
    license_plate = data.get("license_plate")
    username = data.get("username")

    if not username or not license_plate:
        return jsonify({"code": 400, "message": "缺少必要的参数"}), 400

    # 根据用户名查找用户
    user = User.query.filter_by(phone=username).first()
    print(f"Found user: {user}")  # ✅ 添加调试日志

    if not user or user.role != "visitor":
        return jsonify({"code": 403, "message": "权限不足"}), 403

    # **更新或创建访客通行证**
    if not user.visitor_pass:
        user.visitor_pass = VisitorPass(
            user_id=user.id,
            license_plate=license_plate,
            expires_at=datetime.utcnow() + timedelta(days=7)  # 设置 7 天有效期
        )
    else:
        user.visitor_pass.license_plate = license_plate
        user.visitor_pass.expires_at = datetime.utcnow() + timedelta(days=7)

    db.session.commit()

    return jsonify({"success": True, "message": "访客通行证更新成功"})




@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh_access_token():
    """使用 Refresh Token 获取新 Access Token"""
    identity = get_jwt_identity()  # ✅ 直接获取 identity
    new_token = create_access_token(identity=identity)
    return jsonify({
        "code": 200,
        "msg": "令牌刷新成功",
        "access_token": new_token
    }), 200


from app.extensions import redis_client  # ✅ 确保 redis_client 可用

@auth_bp.route('/logout', methods=['DELETE'])
@jwt_required()
def logout():
    """用户登出"""
    try:
        jti = get_jwt()["jti"]
        expires_in = get_jwt()["exp"] - get_jwt()["iat"]

        # **检查 Redis 是否可用**
        if not redis_client.ping():
            return jsonify({"code": 500, "msg": "Redis 连接失败"}), 500
        
        redis_client.setex(jti, expires_in, "revoked")

    except Exception as e:
        print(f"Logout Error: {e}")  # ✅ 打印错误信息
        return jsonify({"code": 500, "msg": "登出失败"}), 500

    return jsonify({"code": 200, "msg": "成功登出"}), 200

from flask_jwt_extended import jwt_required, get_jwt_identity  # 导入必要的函数
from flask import jsonify

@auth_bp.route('/info', methods=['GET'])
@jwt_required()
def user_info():
    try:
        user_id = get_jwt_identity()
        print("Fetching user data...")
        # 使用更高效的查询方式（避免加载无关字段）
        # 使用 JOIN 连接查询用户和车辆信息
        user = db.session.query(
            User.id,
            User.name,
            User.phone,
            User.role,
            User.school_id,
            ElectricVehicle.plate_number.label('license_plate')  # 获取电动车的车牌号
        ).join(
            ElectricVehicle, ElectricVehicle.owner_id == User.id, isouter=True  # 外连接，确保即使没有车辆也能获取到用户信息
        ).filter(User.id == user_id).first()
        
        if not user:
            return jsonify({"code": 404, "msg": "用户未找到"}), 404

        return jsonify({
            "code": 200,
            "msg": "获取成功",
            "data": {
                "user_id": user.id,
                "name": user.name,
                "phone": user.phone,
                "role": user.role,
                'school_id': user.school_id,
                'license_plate': user.license_plate
            }
        }),200, {'Content-Type': 'application/json; charset=utf-8'}
    except Exception as e:
        print(f"Error in user_info: {e}")
        return jsonify({"code": 500, "msg": "服务器内部错误"}), 500



@auth_bp.route('/admin_users', methods=['GET'])
# @role_required('admin')  # ✅ 管理员权限
@jwt_required()
def get_all_users():
    users = User.query.all()  # 查询所有用户
    return jsonify({
        "code": 200,
        "data": [
            {
                "user_id": user.id,
                "name": user.name,
                "phone": user.phone,
                "role": user.role,
                'school_id': user.school_id,
                'license_plate': user.license_plate
            } 
            for user in users
        ]
    })

@auth_bp.route('/info', methods=['OPTIONS', 'GET'])
@jwt_required()
def get_user_info():
    if request.method == "OPTIONS":
        return '', 200  # 处理 CORS 预检请求
    
    current_user = get_jwt_identity()
    return jsonify({"user": current_user}), 200


@auth_bp.route("/getVisitorInfo", methods=["GET"])
@jwt_required()  # 需要用户登录
def get_visitor_info():
    # 获取当前用户的身份信息
    user_id = get_jwt_identity()  # 从 JWT 中获取当前用户 ID
    user = User.query.get(user_id)  # 根据 ID 获取用户信息

    # 判断用户是否是访客
    if not user or user.role != "visitor":
        return jsonify({"code": 403, "message": "权限不足"}), 403

    # 查找访客的通行证信息
    visitor_pass = VisitorPass.query.filter_by(user_id=user.id).first()

    # 构建访客信息的响应
    visitor_info = {
        "name": user.name,  # 用户的姓名
        "phone": user.phone,  # 用户的手机号
        "role": user.role,  # 用户的角色
        "license_plate": visitor_pass.license_plate if visitor_pass else "无车牌号",  # 车牌号
        "created_at": visitor_pass.created_at if visitor_pass else None,  # 通行证创建时间
        "expires_at": visitor_pass.expires_at if visitor_pass else None  # 通行证失效时间
    }

    return jsonify({"success": True, "data": visitor_info}), 200





