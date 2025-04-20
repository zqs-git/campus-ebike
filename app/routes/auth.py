# app/routes/auth.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    get_jwt, jwt_required, get_jwt_identity
)
from werkzeug.security import generate_password_hash
from app.models.users import User, VisitorPass
from app.models.vehicles import ElectricVehicle
from app import db
from sqlalchemy.exc import IntegrityError, OperationalError
from datetime import datetime, timedelta
import logging

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

# --------------------------
# 注册接口
# --------------------------
@auth_bp.route('/register', methods=['POST'])
def register():
    """
    支持校内人员（student/staff）和校外访客（visitor）注册
    """
    data = request.get_json()
    print(f"Received registration data: {data}")
    if not data:
        return jsonify({"msg": "没有收到数据"}), 400

    role = data.get('role')
    print(f"Received role: {role}")
    license_plate = data.get('license_plate', None)
    print(f"Received license plate: {license_plate}")

    # 基础参数校验
    if role not in ['student', 'staff', 'admin', 'visitor']:
        return jsonify({"code": 400, "msg": "无效的角色"}), 400

    if not data.get('password') or len(data['password']) < 6:
        return jsonify({"code": 400, "msg": "密码需6位以上"}), 400

    # 分角色校验
    if role in ['student', 'staff']:
        if not data.get('school_id'):
            return jsonify({"code": 400, "msg": "学工号不能为空"}), 400
        # 模拟验证
        if not validate_school_info(data['school_id'], data.get('name')):
            return jsonify({"code": 403, "msg": "学工号验证失败"}), 403
        if User.query.filter_by(school_id=data['school_id']).first():
            return jsonify({"code": 409, "msg": "该学工号已注册"}), 409

    if role == 'visitor':
        if not data.get('id_card') or not data.get('license_plate'):
            return jsonify({"code": 400, "msg": "身份证号和车牌号不能为空"}), 400
        print(f"Validating ID card: {data['id_card']}")
        print(f"Validating license plate: {data['license_plate']}")

    try:
        new_user = User(
            school_id=data.get('school_id') if role in ['student', 'staff'] else None,
            password=data['password'],  # 模型中可自动加密
            phone=data.get('phone'),
            name=data.get('name'),
            id_card=data.get('id_card') or None,
            role=role
        )
        if role == 'visitor':
            if not license_plate:
                return jsonify({"code": 400, "msg": "访客必须提供车牌号"}), 400
            new_user.license_plate = license_plate

        print(f"New user object: {new_user}")
        db.session.add(new_user)
        db.session.commit()

        return jsonify({
            "code": 201,
            "msg": "注册成功",
            "data": {
                "user_id": new_user.id,
                "role": new_user.role,
            }
        }), 201

    except IntegrityError as e:
        db.session.rollback()
        print(f"IntegrityError: {e}")
        return jsonify({'error': 'IntegrityError', 'details': str(e)}), 400

    except OperationalError as e:
        db.session.rollback()
        print(f"OperationalError: {e}")
        return jsonify({'error': 'OperationalError', 'details': str(e)}), 500

    except Exception as e:
        db.session.rollback()
        print(f"Unknown Error: {e}")
        return jsonify({'error': 'Registration failed', 'details': str(e)}), 500


# 模拟验证服务
def validate_school_info(school_id, name):
    return True if school_id.startswith('20') else False

def validate_id_card(id_number):
    return len(id_number) == 18


# --------------------------
# 登录接口
# --------------------------
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not isinstance(data, dict):
        return jsonify({"code": 400, "msg": "请求数据格式错误"}), 400

    username = (data.get("username") or "").strip().lower()
    password = data.get("password") or ""
    if not username or not password:
        return jsonify({"code": 400, "msg": "请求必须包含用户名和密码"}), 400

    logging.info(f"查询用户名: {username}")
    user = User.query.filter(
        (User.phone == username) | (User.school_id == username)
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

    # 访客通行证过期处理
    if user.role == 'visitor' and not user.is_visitor_pass_valid():
        logging.warning(f"❌ 用户 {user.id} 的访客通行证已过期，无法登录")
        db.session.rollback()
        return jsonify({
            "code": 403,
            "msg": "您的通行证已过期，请更新通行证",
            "need_update": True,
            "user_info": {
                "license_plate": user.license_plate or ''
            }
        }), 403

    access_token = create_access_token(identity=str(user.id), additional_claims={"role": user.role})
    refresh_token = create_refresh_token(identity=str(user.id))
    user.last_login = datetime.now()

    try:
        db.session.commit()
        logging.info("✅ 登录时间已成功更新")
    except Exception as e:
        db.session.rollback()
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


# --------------------------
# 访客通行证更新接口
# --------------------------
@auth_bp.route("/updateVisitorPass", methods=["POST"])
def update_visitor_pass():
    data = request.json
    print(f"Received data: {data}")
    license_plate = data.get("license_plate")
    username = data.get("username")

    if not username or not license_plate:
        return jsonify({"code": 400, "message": "缺少必要的参数"}), 400

    user = User.query.filter_by(phone=username).first()
    print(f"Found user: {user}")
    if not user or user.role != "visitor":
        return jsonify({"code": 403, "message": "权限不足"}), 403

    if not user.visitor_pass:
        user.visitor_pass = VisitorPass(
            user_id=user.id,
            license_plate=license_plate,
            expires_at=datetime.utcnow() + timedelta(days=7)
        )
    else:
        user.visitor_pass.license_plate = license_plate
        user.visitor_pass.expires_at = datetime.utcnow() + timedelta(days=7)

    db.session.commit()

    return jsonify({"success": True, "message": "访客通行证更新成功"})


# --------------------------
# Refresh Token 接口
# --------------------------
@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh_access_token():
    identity = get_jwt_identity()
    new_token = create_access_token(identity=identity)
    return jsonify({
        "code": 200,
        "msg": "令牌刷新成功",
        "access_token": new_token
    }), 200


from app.extensions import redis_client

# --------------------------
# 登出接口
# --------------------------
@auth_bp.route('/logout', methods=['DELETE'])
@jwt_required()
def logout():
    try:
        jti = get_jwt()["jti"]
        expires_in = get_jwt()["exp"] - get_jwt()["iat"]
        if not redis_client.ping():
            return jsonify({"code": 500, "msg": "Redis 连接失败"}), 500
        redis_client.setex(jti, expires_in, "revoked")
    except Exception as e:
        print(f"Logout Error: {e}")
        return jsonify({"code": 500, "msg": "登出失败"}), 500
    return jsonify({"code": 200, "msg": "成功登出"}), 200


from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import jsonify

# --------------------------
# 获取用户信息接口
# --------------------------
@auth_bp.route('/info', methods=['GET'])
@jwt_required()
def user_info():
    try:
        user_id = get_jwt_identity()
        print("Fetching user data...")
        user = db.session.query(
            User.id,
            User.name,
            User.phone,
            User.role,
            User.school_id,
            ElectricVehicle.plate_number.label('license_plate')
        ).join(
            ElectricVehicle, ElectricVehicle.owner_id == User.id, isouter=True
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
                "school_id": user.school_id,
                "license_plate": user.license_plate
            }
        }), 200, {'Content-Type': 'application/json; charset=utf-8'}
    except Exception as e:
        print(f"Error in user_info: {e}")
        return jsonify({"code": 500, "msg": "服务器内部错误"}), 500


# --------------------------
# 获取所有用户信息接口
# --------------------------
@auth_bp.route('/admin_users', methods=['GET'])
@jwt_required()
def get_all_users():
    users = User.query.all()
    return jsonify({
        "code": 200,
        "data": [
            {
                "user_id": user.id,
                "name": user.name,
                "phone": user.phone,
                "role": user.role,
                "school_id": user.school_id,
                "license_plate": user.license_plate
            }
            for user in users
        ]
    })


@auth_bp.route('/info', methods=['OPTIONS', 'GET'])
@jwt_required()
def get_user_info():
    if request.method == "OPTIONS":
        return '', 200
    current_user = get_jwt_identity()
    return jsonify({"user": current_user}), 200


# --------------------------
# 获取访客信息接口
# --------------------------
@auth_bp.route("/getVisitorInfo", methods=["GET"])
@jwt_required()
def get_visitor_info():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or user.role != "visitor":
        return jsonify({"code": 403, "message": "权限不足"}), 403

    visitor_pass = VisitorPass.query.filter_by(user_id=user.id).first()
    visitor_info = {
        "name": user.name,
        "phone": user.phone,
        "role": user.role,
        "license_plate": visitor_pass.license_plate if visitor_pass else "无车牌号",
        "created_at": visitor_pass.created_at if visitor_pass else None,
        "expires_at": visitor_pass.expires_at if visitor_pass else None
    }

    return jsonify({"success": True, "data": visitor_info}), 200


# --------------------------
# 更新用户信息接口
# --------------------------
@auth_bp.route('/info/update', methods=['PUT'])
@jwt_required()
def update_user_info():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({"code": 404, "msg": "用户未找到"}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({"code": 400, "msg": "无效的请求数据"}), 400
        
        new_name = data.get('name', '').strip()
        new_school_id = data.get('school_id', '').strip()
        new_phone = data.get('phone', '').strip()

        if not new_name:
            return jsonify({"code": 400, "msg": "姓名不能为空"}), 400

        if user.role in ['student', 'staff'] and not new_school_id:
            return jsonify({"code": 400, "msg": "学号不能为空"}), 400

        import re
        phone_pattern = re.compile(r'^1[3-9]\d{9}$')
        if not phone_pattern.match(new_phone):
            return jsonify({"code": 400, "msg": "手机号格式不正确"}), 400

        if new_phone != user.phone:
            existing_user_with_phone = User.query.filter_by(phone=new_phone).first()
            if existing_user_with_phone:
                return jsonify({"code": 409, "msg": "该手机号已被其他用户使用"}), 409

        if user.role in ['student', 'staff'] and new_school_id != user.school_id:
            existing_user = User.query.filter_by(school_id=new_school_id).first()
            if existing_user:
                return jsonify({"code": 409, "msg": "该学号已被其他用户使用"}), 409
        
        user.name = new_name or user.name
        user.school_id = new_school_id or user.school_id
        user.phone = new_phone or user.phone
        
        db.session.commit()
        
        return jsonify({
            "code": 200,
            "msg": "更新成功",
            "data": {
                "user_id": user.id,
                "name": user.name,
                "school_id": user.school_id,
                "phone": user.phone,
                "role": user.role,
                "license_plate": user.license_plate
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"code": 500, "msg": "服务器内部错误", "error": str(e)}), 500
    
# --------------------------
# 删除用户接口
# --------------------------
@auth_bp.route('/admin/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"code": 404, "msg": "用户不存在"}), 404
    # 删除前处理关联数据
    if user.visitor_pass:
        db.session.delete(user.visitor_pass)
    db.session.delete(user)
    try:
        db.session.commit()
        return jsonify({"code": 200, "msg": "账户删除成功"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"code": 500, "msg": "账户删除失败", "error": str(e)}), 500


