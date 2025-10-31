from functools import wraps
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt

def get_current_user_role():
    """
    Obtiene el rol del usuario actual desde el JWT
    """
    try:
        claims = get_jwt()
        return claims.get('role', 'user')
    except:
        return None

def role_required(f):
    """Decorator que requiere autenticación JWT válida"""
    @wraps(f)
    @jwt_required()
    def decorated_fn(*args, **kwargs):
        current_role = get_current_user_role()
        print(current_role)
        if current_role is None:
            return jsonify({
                'error': 'Permisos insuficientes',
                'message': f'Se requiere autenticación válida. Tu rol: {current_role}'
            }), 403
        return f(*args, **kwargs)
    return decorated_fn

def admin_required(f):
    """
    Decorator específico para endpoints que solo pueden acceder administradores
    """
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        current_role = get_current_user_role()
        
        if current_role != 'admin':
            return jsonify({
                'error': 'Acceso denegado',
                'message': 'Solo los administradores pueden acceder a este endpoint'
            }), 403
        
        return f(*args, **kwargs)
    return decorated_function