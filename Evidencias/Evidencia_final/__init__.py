from flask import Flask
from flask_jwt_extended import JWTManager
from config import config
from app.models import init_db, initialize_users, initialize_cars

# Instancias globales
jwt = JWTManager()

def create_app(config_name='default'):
    """Factory para crear la aplicación Flask"""
    app = Flask(__name__)
    
    # Cargar configuración
    app.config.from_object(config[config_name])
    
    # Inicializar extensiones
    jwt.init_app(app)
    
    # Inicializar base de datos
    init_db(app.config['MONGO_URI'], app.config['DATABASE_NAME'])
    
    # Inicializar datos por defecto
    initialize_users()
    initialize_cars()
    
    # Registrar blueprints
    from app.routes.auth import auth_bp
    from app.routes.cars import car_bp
    from app.routes.pages import pages_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(car_bp, url_prefix='/car')
    app.register_blueprint(pages_bp)
    
    return app