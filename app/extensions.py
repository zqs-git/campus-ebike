# app/extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
import redis
from flask_redis import FlaskRedis  # ✅ 使用 Flask-Redis
from flask_socketio import SocketIO

db = SQLAlchemy()
# migrate = Migrate()  # ⭐ 在此处创建迁移实例

jwt = JWTManager()
redis_client = FlaskRedis()  # ✅ 兼容 Flask 的 Redis
socketio = SocketIO(cors_allowed_origins="*")

def init_extensions(app):
    """初始化所有第三方扩展"""
    db.init_app(app)
    redis_client.init_app(app)
    jwt.init_app(app)