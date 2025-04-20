from flask import request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

def init_security(app):
    """初始化安全相关配置"""
    # 登录接口限流（5次/分钟）
    limiter.limit("5/minute")(auth_bp.decorators)
    
    # 密码复杂度规则
    PASSWORD_POLICY = {
        'min_length': 8,
        'require_uppercase': True,
        'require_lowercase': True,
        'require_digits': True,
        'require_special': True
    }