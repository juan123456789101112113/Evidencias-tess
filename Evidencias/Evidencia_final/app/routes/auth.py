from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from app.models import authenticate_user

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Endpoint para iniciar sesión y obtener JWT token
    
    Body JSON requerido:
    {
        "username": "string",
        "password": "string"
    }
    """
    if not request.json or 'username' not in request.json or 'password' not in request.json:
        return jsonify({
            'error': 'Datos inválidos',
            'message': 'Se requieren username y password'
        }), 400
    
    username = request.json['username']
    password = request.json['password']
    
    # Autenticar usuario
    user, error_response, status_code = authenticate_user(username, password)
    if error_response:
        return jsonify(error_response), status_code
    
    # Crear token JWT
    user_id = user.get('user_id') or user.get('id')  # Compatibilidad con ambos formatos
    access_token = create_access_token(
        identity=username,
        additional_claims={
            'role': user['role'],
            'user_id': user_id
        }
    )
    
    return jsonify({
        'message': 'Login exitoso',
        'access_token': access_token,
        'user': {
            'id': user_id,
            'username': user['username'],
            'role': user['role']
        }
    })