from flask import Flask
from .config import Config
from .extensions import db
from flask_migrate import Migrate


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # 初始化数据库
    db.init_app(app)
    # 初始化迁移扩展
    migrate = Migrate(app, db)
    from .models import User  # 🔥 确保导入模型，否则 `flask db migrate` 可能检测不到

    from .routes import main_bp, test_bp  # 确保导入 test_bp
    app.register_blueprint(main_bp)  # 注册主路由
    app.register_blueprint(test_bp)  # 注册测试路由

    return app