from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt, verify_jwt_in_request

def role_required(*allowed_roles):
    """
    角色权限验证装饰器
    参数:
        allowed_roles (str): 允许访问该接口的角色列表，如 ('admin', 'staff')
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 验证 JWT 有效性
            verify_jwt_in_request()
            # 获取 JWT 的 claims（包括 role 字段）
            claims = get_jwt()
            user_role = claims.get("role", "")  # 默认空字符串避免 KeyError
            # 检查用户角色是否在允许的列表中
            if user_role not in allowed_roles:
                return jsonify({"code": 403, "msg": "无权限访问该资源"}), 403
            # 角色验证通过，执行原函数
            return func(*args, **kwargs)
        return wrapper
    return decorator