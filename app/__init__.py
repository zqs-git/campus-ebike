# app/__init__.py
from flask import Flask
from .config import Config, TestingConfig, DevelopmentConfig, ProductionConfig
from flask_migrate import Migrate
from .extensions import db,init_extensions,redis_client  # 从扩展文件导入
import redis
from datetime import timedelta
from flask_jwt_extended import JWTManager
jwt = JWTManager()

# 定义配置映射字典（配置名称 → 配置类）
config_mapping = {
    'testing': TestingConfig,
    'development': DevelopmentConfig,
    'production': ProductionConfig
}

# 全局扩展对象（需在此处声明）
migrate = Migrate()


def create_app(config_name='development'):
    """
    Flask应用工厂函数
    参数:
        config_name (str): 指定配置环境（testing/development/production）
    """
    # 创建Flask应用实例
    app = Flask(__name__)
    
    # --------------------------
    # 配置加载
    # --------------------------
    try:
        # 根据配置名称加载对应配置类
        app.config.from_object(config_mapping[config_name])
    except KeyError:
        raise ValueError(f"Invalid config name: {config_name}. "
                         f"Valid options: {list(config_mapping.keys())}")

    # 初始化扩展
    init_extensions(app)
    app.config["REDIS_URL"] = "redis://localhost:6379/0"  # ✅ 配置 Redis 连接
    
    # 绑定迁移实例到应用和数据库
    migrate.init_app(app, db)  # ✅ 关键修正

    from app.models import users  # 或者具体的模型模块

    # JWT回调配置
    @jwt.user_lookup_loader
    def user_loader_callback(_jwt_header, jwt_data):
        """根据JWT identity加载用户"""
        identity = jwt_data["sub"]
        return User.query.get(identity)

    @jwt.token_in_blocklist_loader
    def check_token_revoked(jwt_header, jwt_data):
        """检查令牌是否在黑名单"""
        jti = jwt_data["jti"]
        return redis_client.exists(jti) == 1
    # --------------------------
    # 蓝图注册（延迟导入避免循环依赖）
    # --------------------------
    register_blueprints(app)



    return app

def register_blueprints(app):
    """集中注册所有路由蓝图"""
    from .routes.auth import auth_bp
    from .routes.main import main_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    
    # 测试专用路由（仅在开发/测试环境加载）
    if app.config.get('DEBUG') or app.config.get('TESTING'):
        from .routes.main import test_bp  # 测试蓝图按需导入
        app.register_blueprint(test_bp)