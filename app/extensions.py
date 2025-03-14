# app/extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
# migrate = Migrate()  # ⭐ 在此处创建迁移实例