from flask import Flask, request, jsonify
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash 
from flask_jwt_extended import JWTManager, jwt_required, get_jwt, create_access_token
from functools import wraps

app = Flask(__name__)

jwt = JWTManager(app)
app.config['JWT_SECRET_KEY'] = 'tu-clave-super-secreta-cambiar-en-produccion'  # ¡Cambiar en producción!
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)

users = {"manager": {
                    'id': 'user-2',
                    'username': 'manager',
                    'password_hash': generate_password_hash('manager123'),  # Password: manager123
                    'role': 'manager',
                    'created_at': '2024-01-15T11:00:00Z'
                    },
        "admin1":    {'id': 'user-1',
                    'username': 'admin1',
                    'password_hash': generate_password_hash('admin123'),  # Password: manager123
                    'role': 'admin',
                    'created_at': '2024-01-15T11:00:00Z'
                    },
        "client":    {'id': 'user-3',
                    'username': 'client1',
                    'password_hash': generate_password_hash('client123'),  # Password: manager123
                    'role': 'client',
                    'created_at': '2024-01-15T11:00:00Z'
                    }
}


@app.route('/auth/login', methods=['POST'])
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
    
    # Verificar si el usuario existe
    user = users.get(username)
    print(user)
    if not user or not check_password_hash(user['password_hash'], password):
        return jsonify({
            'error': 'Credenciales inválidas',
            'message': 'Username o password incorrectos'
        }), 401
    
    # Crear token JWT
    access_token = create_access_token(
        identity=username,
        additional_claims={
            'role': user['role'],
            'user_id': user['id']
        }
    )
    
    return jsonify({
        'message': 'Login exitoso',
        'access_token': access_token,
        'user': {
            'id': user['id'],
            'username': user['username'],
            'role': user['role']
        }
    })

carros = [
    {'id': 1, 'marca': 'Toyota', 'modelo': 'Corolla', 'año': 2020},
    {'id': 2, 'marca': 'Honda', 'modelo': 'Civic', 'año': 2019},
    {'id': 3, 'marca': 'Ford', 'modelo': 'Focus', 'año': 2018},
    {'id': 4, 'marca': 'Volkswagen', 'modelo': 'Golf', 'año': 2019},
    {'id': 5, 'marca': 'Chevrolet', 'modelo': 'Cruze', 'año': 2022}
]

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
    @wraps(f)
    @jwt_required()
    def decorated_fn(*args, **kwargs):
        current_role = get_current_user_role()
        if current_role is None:
            return jsonify({
                'error': 'Permisos insuficientes',
                'message': f'Se requiere uno de estos roles: {", ".join(required_roles)}. TuTu rol: {current_role}'
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

@app.route('/carros/', methods=['GET'])
@role_required
def filter_carros():
    marca_query_param = request.args.get("marca")
    modelo_query_param = request.args.get("modelo")
    print(f"marca {marca_query_param}, modelo {modelo_query_param}")
    ans = carros
    if marca_query_param is not None:
        ans = list(filter(lambda x: x ["marca"] == marca_query_param, ans))
    if modelo_query_param is not None:
        ans = list(filter(lambda x: x ["modelo"] == modelo_query_param, ans))
    return ans, 200

@app.route('/carros/<string:carro_id>/', methods=['GET'])
@role_required
def get_carro(carro_id):
    ans = list(filter(lambda x: x ["id"] == int(carro_id), carros))
    if len(ans) > 0:
        return ans[0], 200
    else:
        return {"mensaje": "Carro no existe"}, 404

@app.route('/carros/', methods=['POST'])
@admin_required
def post_carro():
    print(f"body: {request.json}")
    body = request.json
    new_carro ={
            "id": body["id"],
            "marca": body["marca"],
            "modelo": body["modelo"],
            "año": body["año"],
    }
    carros.append(new_carro)
    return new_carro, 201

@app.route('/new_user', methods=['POST'])
@admin_required
def create_new_user():
    print(f"body: {request.json}")
    body = request.json
    new_carro ={
            'id': body["id"],
            'username': body["username"],
            'password_hash': generate_password_hash(body["password_hash"]),
            'role': body["role"],
            'created_at': body["created_at"]
    }
    carros.append(new_carro)
    return new_carro, 201

@app.route('/carros/<string:carro_id>/', methods=['DELETE'])
@admin_required
def delete_carro(carro_id):
    global carros
    carros = list(filter(lambda x: x["id"] != int(carro_id), carros))
    return f"se borro el carro de id: {carro_id}", 204


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=8003,
        debug=True
    )