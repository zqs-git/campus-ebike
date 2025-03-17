# app/routes/__init__.py
def init_app(app):
    from .main import main_bp
    from .auth import auth_bp
    from .vehicles import vehicle_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(vehicle_bp, url_prefix='/api/vehicle')

    print("Vehicle routes registered successfully")
