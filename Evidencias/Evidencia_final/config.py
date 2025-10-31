import os
from datetime import timedelta

class Config:
    """Configuración base"""
    # Claves secretas
    SECRET_KEY = os.getenv('SECRET_KEY')
    
    # JWT Configuration
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    
    # MongoDB Configuration
    MONGO_URI = os.getenv('MONGO_URI')
    DATABASE_NAME = os.getenv('DATABASE_NAME')
    
    # Server Configuration
    HOST = os.getenv('HOST')
    PORT = int(os.getenv('PORT', 0))
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'

class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    DEBUG = True
    
class ProductionConfig(Config):
    """Configuración para producción"""
    DEBUG = False
    # En producción, estas deberían venir de variables de entorno
    SECRET_KEY = os.getenv('SECRET_KEY', Config.SECRET_KEY)
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', Config.JWT_SECRET_KEY)

class TestingConfig(Config):
    """Configuración para testing"""
    TESTING = True
    DATABASE_NAME = 'flask_app_test'

# Diccionario de configuraciones
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}