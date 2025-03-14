"""
应用程序配置文件
通过环境变量实现多环境（开发/测试/生产）配置切换
"""

import os
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量（本地开发使用）
load_dotenv()

class Config:
    """
    基础配置类（所有环境共享配置）
    敏感配置应从环境变量读取，不要硬编码
    """
    # --------------------------
    # 安全配置
    # --------------------------
    
    # Flask加密密钥，用于会话签名等安全功能
    # 生产环境必须通过环境变量设置（FLASK_SECRET_KEY）
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-key')  
    
    # --------------------------
    # 数据库配置（生产环境需覆盖）
    # --------------------------
    
    # 使用pymysql连接MySQL（格式：mysql+pymysql://用户:密码@主机:端口/数据库）
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{os.getenv('DB_USER')}:"
        f"{os.getenv('DB_PASSWORD')}@"
        f"{os.getenv('DB_HOST')}:"
        f"{os.getenv('DB_PORT')}/"
        f"{os.getenv('DB_NAME')}"
    )
    
    # 禁用SQLAlchemy事件系统（节省资源）
    SQLALCHEMY_TRACK_MODIFICATIONS = False  
    
    # 数据库连接池配置（优化高并发性能）
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,    # 每次使用前检查连接活性
        "pool_recycle": 300,     # 连接回收时间（秒），需小于数据库wait_timeout
        "pool_size": 20,         # 保持打开的连接数
        "max_overflow": 30       # 允许临时增加的连接数（高峰期）
    }

    # --------------------------
    # JWT认证配置
    # --------------------------
    
    # JWT签名密钥（需与Flask SECRET_KEY不同）
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-dev-key')  

    # --------------------------
    # 文件存储配置
    # --------------------------
    
    # 文件上传保存路径（生产环境应使用云存储）
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')


# config.py
import sqlalchemy

class TestingConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    TESTING = True
    
    # SQLite专用优化
    if 'sqlite' in SQLALCHEMY_DATABASE_URI:
        SQLALCHEMY_ENGINE_OPTIONS = {
            "connect_args": {"check_same_thread": False},
            "poolclass": sqlalchemy.NullPool
        }
    else:
        # 其他数据库保留原配置
        SQLALCHEMY_ENGINE_OPTIONS = {
            **Config.SQLALCHEMY_ENGINE_OPTIONS,
            "pool_pre_ping": True,
            "pool_recycle": 300
        }


class DevelopmentConfig(Config):
    """
    开发环境配置
    开启调试功能和详细日志
    """
    # 启用调试模式（自动重载代码、显示错误详情）
    DEBUG = True  
    
    # 打印所有SQL语句（调试数据库操作）
    SQLALCHEMY_ECHO = True  


class ProductionConfig(Config):
    """
    生产环境配置
    强调性能和安全性
    """
    # 强制关闭调试模式
    DEBUG = False  
    
    # 优化数据库连接池（根据服务器配置调整）
    SQLALCHEMY_ENGINE_OPTIONS = {
        **Config.SQLALCHEMY_ENGINE_OPTIONS,
        "pool_size": 50,       # 增加常驻连接数
        "max_overflow": 100    # 允许更大的临时连接数
    }