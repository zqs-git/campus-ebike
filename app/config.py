import os
from dotenv import load_dotenv

load_dotenv()  # 确保加载.env文件

class Config:
    # --------------------------
    # 基础配置（所有环境共享）
    # --------------------------
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-key')  # 优先从环境变量读取
    DEBUG = os.getenv('FLASK_DEBUG', 'False') == 'True'    # 默认关闭调试模式

    # --------------------------
    # 数据库配置
    # --------------------------
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
        "pool_size": 20,
        "max_overflow": 30
    }

    # --------------------------
    # 其他配置（按需添加）
    # --------------------------
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-dev-key')
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')

# 环境特定配置（继承基础配置）
class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True  # 显示SQL日志

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        **Config.SQLALCHEMY_ENGINE_OPTIONS,
        "pool_size": 50,
        "max_overflow": 100
    }