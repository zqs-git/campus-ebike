# app/routes/__init__.py
def init_app(app):
    from .main import main_bp
    from .auth import auth_bp
    from .vehicles import vehicle_bp
    from .parking import parking_bp
    from .location import location_bp
    from .location import locations_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(vehicle_bp, url_prefix='/api/vehicle')
    app.register_blueprint(parking_bp, url_prefix='/api/parking')
    app.register_blueprint(location_bp, url_prefix='/api/location')
    app.register_blueprint(locations_bp, url_prefix='/api/locations')



    print("Vehicle routes registered successfully")
