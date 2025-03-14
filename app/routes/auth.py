# app/routes/auth.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token,get_jwt,jwt_required,current_user  
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from app.models.users import User
from app import db
from sqlalchemy.exc import IntegrityError, OperationalError

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
    # print(f"Received registration data: {data}")  # ✅ 添加调试日志
    if not data:
        return jsonify({"msg": "没有收到数据"}), 400
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
            id_card=data.get('id_card') or None,
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


# @auth_bp.route('/login', methods=['POST'])
# def login():
    """
    用户登录接口
    ---
    tags:
      - 认证
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            username:
              type: string
              description: 手机号或学工号
              example: "13800138000"
            password:
              type: string
              description: 登录密码
              example: "TestPass123!"
    responses:
      200:
        description: 登录成功返回令牌
      400:
        description: 请求参数缺失
      401:
        description: 用户名或密码错误
    """
    # 获取请求数据
    data = request.get_json()
    print(f"Received JSON: {data}")  # ✅ 确保数据正确
    
    # 参数校验
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({"code": 400, "msg": "请求必须包含用户名和密码"}), 400
    
    username = data['username'].strip().lower()
    password = data['password']
    
    # 查询用户（支持手机号/学工号登录）
    user = User.query.filter(
        (User.phone == username) | 
        (User.school_id == username)
    ).first()
    
    # 用户不存在或密码错误
    if not user or not user.verify_password(password):
        return jsonify({"code": 401, "msg": "用户名或密码错误"}), 401
    
    # 账户状态检查
    if not user.is_active:
        return jsonify({"code": 403, "msg": "账户已被禁用"}), 403
    
    # 生成JWT令牌
    access_token = create_access_token(identity=user)
    refresh_token = create_refresh_token(identity=user)
    
    # 更新登录时间
    user.update_login_time()
    db.session.commit()
    
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

    # 查询用户
    user = User.query.filter(
        (User.phone == username) | 
        (User.school_id == username)
    ).first()
    
    if not user:
        return jsonify({"code": 401, "msg": "用户名或密码错误"}), 401
    
    if not user.is_active:
        return jsonify({"code": 403, "msg": "账户已被禁用"}), 403
    
    if not user.verify_password(password):
        return jsonify({"code": 401, "msg": "用户名或密码错误"}), 401

    # 生成 JWT 令牌
    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)

    user.update_login_time()
    db.session.commit()
    
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



@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh_access_token():
    """使用Refresh Token获取新Access Token"""
    new_token = create_access_token(identity=current_user)
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
