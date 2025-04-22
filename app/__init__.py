from flask import Flask, request
from .config import Config, TestingConfig, DevelopmentConfig, ProductionConfig
from flask_migrate import Migrate
from .extensions import db, init_extensions, redis_client
from flask_jwt_extended import JWTManager
from flask_cors import CORS
import logging
from logging.handlers import RotatingFileHandler
from .permissions import role_required  # 可选，全局导入权限装饰器

# 全局扩展对象
jwt = JWTManager()
migrate = Migrate()

# 配置映射
config_mapping = {
    'testing': TestingConfig,
    'development': DevelopmentConfig,
    'production': ProductionConfig
}

def create_app(config_name='development'):
    """
    Flask 应用工厂函数
    参数:
        config_name (str): 指定配置环境（testing/development/production）
    """
    app = Flask(__name__)

    # --------------------------
    # 加载配置
    # --------------------------
    try:
        app.config.from_object(config_mapping[config_name])
    except KeyError:
        raise ValueError(f"Invalid config name: {config_name}. "
                         f"Valid options: {list(config_mapping.keys())}")

    # 设置 Redis URL（可以提取到 config 中更好）
    app.config["REDIS_URL"] = "redis://localhost:6379/0"

    # --------------------------
    # 启用 CORS
    # --------------------------
    # 允许所有来源的跨域请求
    CORS(app, supports_credentials=True)

    # --------------------------
    # 初始化扩展
    # --------------------------
    init_extensions(app)
    jwt.init_app(app)  # 使用统一声明的 jwt
    migrate.init_app(app, db)

    # --------------------------
    # 日志配置（仅开发环境启用）
    # --------------------------
    if app.debug:
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        sql_logger = logging.getLogger('sqlalchemy.engine')
        sql_logger.setLevel(logging.INFO)

        file_handler = RotatingFileHandler(
            'app.log', maxBytes=1024*1024, backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        app.logger.addHandler(file_handler)

    # --------------------------
    # 注册模型（确保被 Alembic 识别）
    # --------------------------
    from app.models import users
    from app.models.users import User
    from app.models.vehicles import ElectricVehicle
    from app.models.location import CampusLocation
    from app.models.parking import ParkingLot, ParkingSpace, ParkingRecord
    from app.models.charging import ChargingPile, ChargingSession,ChargingSessionStatus, ChargingPileStatus

    # --------------------------
    # JWT 回调配置
    # --------------------------
    @jwt.user_lookup_loader
    def user_loader_callback(_jwt_header, jwt_data):
        """根据 JWT identity 加载用户"""
        identity = jwt_data["sub"]
        print("JWT 解析的 identity:", identity)
        return User.query.get(int(identity)) if identity.isdigit() else None

    @jwt.token_in_blocklist_loader
    def check_token_revoked(jwt_header, jwt_data):
        """检查令牌是否被加入黑名单"""
        jti = jwt_data["jti"]
        return redis_client.exists(jti) == 1

    # --------------------------
    # 注册蓝图
    # --------------------------
    register_blueprints(app)

    return app


def register_blueprints(app):
    """集中注册所有路由蓝图"""
    from .routes.auth import auth_bp
    from .routes.main import main_bp
    from .routes.vehicles import vehicle_bp
    from .routes.parking import parking_bp
    from .routes.location import location_bp
    from .routes.location import locations_bp
    from .routes.charging import charging_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(vehicle_bp)
    app.register_blueprint(parking_bp)
    app.register_blueprint(location_bp)
    app.register_blueprint(locations_bp)
    app.register_blueprint(charging_bp)
    
    # 测试专用蓝图（仅开发/测试环境加载）
    if app.config.get('DEBUG') or app.config.get('TESTING'):
        from .routes.main import test_bp
        app.register_blueprint(test_bp)
