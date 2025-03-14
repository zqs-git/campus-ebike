# app/routes/__init__.py
def init_app(app):
    from .main import main_bp  # 新增
    from .auth import auth_bp
    
    app.register_blueprint(main_bp)   # 根路由
    app.register_blueprint(auth_bp, url_prefix='/api/auth')