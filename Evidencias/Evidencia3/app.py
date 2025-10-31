from flask import Flask, request, jsonify, render_template_string
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash 
from flask_jwt_extended import JWTManager, jwt_required, get_jwt, create_access_token
from functools import wraps
from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv
from pathlib import Path
import os

# Cargar archivo .env solo si existe (para desarrollo local)
env_path = Path('.') / '.env'
if env_path.exists():
    load_dotenv(dotenv_path=env_path)

# Obtener variables del entorno con valores por defecto
db_name = os.getenv('MONGO_DB')
host = os.getenv('MONGO_HOST')
port = int(os.getenv('MONGO_PORT', 0))
admin_password = os.getenv('admin_pass')
manager_password = os.getenv('manager_pass')
first_client = os.getenv('first_client_pass')

print(f"host is: {host} and database name is {db_name}")

app = Flask(__name__)

jwt = JWTManager(app)
app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET_KEY")
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = os.getenv("JWT_ACCESS_TOKEN_EXPIRES")

try:
    client = MongoClient(str(host)+":"+str(port)+"/")
    db = client[db_name]
    users_collection = db.users
    cars_collection = db.cars
    # Probar la conexión
    client.admin.command('ping')
    print("✅ Conexión a MongoDB exitosa")
except Exception as e:
    print(f"❌ Error conectando a MongoDB: {e}")
    print("⚠️ La aplicación requiere MongoDB para funcionar correctamente")
    client = None
    db = None

def initialize_users():
    """Inicializar usuarios en MongoDB si no existen"""
    if db is None:
        return

    # Verificar si ya existen usuarios
    if users_collection.count_documents({}) == 0:
        users_data = [
            {
                'id': 'user-2',
                'username': 'manager',
                'password_hash': generate_password_hash(manager_password),
                'role': 'manager',
                'created_at': datetime.now()
            },
            {
                'id': 'user-1',
                'username': 'admin1',
                'password_hash': generate_password_hash(admin_password),
                'role': 'admin',
                'created_at': datetime.now()
            },
            {   
                'id': 'user-3',
                'username': 'client1',
                'password_hash': generate_password_hash(first_client),
                'role': 'client',
                'created_at': datetime.now()
            }
        ]
        users_collection.insert_many(users_data)
        print("✅ Usuarios iniciales creados en MongoDB")

def initialize_cars():
    """Inicializar escritorios en MongoDB si no existen"""
    if db is None:
        return

    # Verificar si ya existen escritorios
    if cars_collection.count_documents({}) == 0:
        cars_data = [
                {'id': 1, 'marca': 'Toyota', 'modelo': 'Corolla', 'año': 2020},
                {'id': 2, 'marca': 'Honda', 'modelo': 'Civic', 'año': 2019},
                {'id': 3, 'marca': 'Ford', 'modelo': 'Focus', 'año': 2018},
                {'id': 4, 'marca': 'Volkswagen', 'modelo': 'Golf', 'año': 2019},
                {'id': 5, 'marca': 'Chevrolet', 'modelo': 'Cruze', 'año': 2022}
        ]

        cars_collection.insert_many(cars_data)
        print("✅ Escritorios iniciales creados en MongoDB")


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
    user, error_response, status_code = authenticate_user(username, password)
    if error_response:
        return error_response, status_code
    
    # Crear token JWT
    user_id = user.get('user_id') or user.get('id')
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
            'id': user['id'],
            'username': user['username'],
            'role': user['role']
        }
    })

def get_user_by_username(username):
    """Obtener usuario por username desde MongoDB"""
    if db is None:
        raise Exception("MongoDB no está disponible. No se puede autenticar usuarios.")

    return users_collection.find_one({"username": username})

def authenticate_user(username, password):
    """
    Autentica un usuario verificando sus credenciales
    
    Returns:
        tuple: (user_data, error_response, status_code)
        - Si es exitoso: (user_data, None, None)
        - Si hay error: (None, error_response, status_code)
    """
    try:
        user = get_user_by_username(username)
        print(user)
        if not user or not check_password_hash(user['password_hash'], password):
            return None, {
                'error': 'Credenciales inválidas',
                'message': 'Username o password incorrectos'
            }, 401
        
        return user, None, None
        
    except Exception as e:
        return None, {
            'error': 'Error de base de datos',
            'message': 'No se puede conectar a la base de datos. Verifique que MongoDB esté ejecutándose.'
        }, 503

def get_user_count():
    """Obtener número total de usuarios"""
    if db is None:
        return 0
    return users_collection.count_documents({})

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

@app.route('/cars', methods=['GET'])
@role_required
def get_all_cars():
    marca_query_param = request.args.get("marca")
    modelo_query_param = request.args.get("modelo")
    print(f"marca {marca_query_param}, modelo {modelo_query_param}")
    
    try:
        cars = get_all_cars_filtered(marca_query_param, marca_query_param)

    # Normalizar la respuesta para mantener compatibilidad
        result = []
        for car in cars:
            car_copy = car.copy()
            if '_id' in car_copy:
                del car_copy['_id']  # Remover ObjectId de MongoDB
            if 'car_id' in car_copy:
                car_copy['id'] = car_copy['car_id']  # Mantener compatibilidad con 'id'
            result.append(car_copy)
            
        return result, 200
    except Exception as e:
        return jsonify({
            'error': 'Error de base de datos',
            'message': f'No se puede conectar a la base de datos. Error: {e}'
        }), 503

def get_all_cars_filtered(marca_filter=None, modelo_filter=None):
    """Obtener todos los escritorios con filtros opcionales"""
    if db is None:
        raise Exception("MongoDB no está disponible. No se pueden consultar")

    # Construir filtro para MongoDB
    filter_query = {}
    if marca_filter:
        filter_query["marca"] = {"$gte": int(marca_filter)}
    if modelo_filter:
        filter_query["modelo"] = {"$gte": int(modelo_filter)}

    return list(cars_collection.find(filter_query))

@app.route('/cars/<string:car_id>/', methods=['GET'])
@role_required
def get_car_by_id(car_id):
    """Obtener escritorio por ID desde MongoDB"""
    if db is None:
        raise Exception("MongoDB no está disponible. No se pueden consu") 
    return cars_collection.find_one({"car_id": int(car_id)})

@app.route('/cars', methods=['POST'])
@admin_required
def add_new_car(car_data):
    """Agregar nuevo carro a MongoDB"""
    if db is None:
        raise Exception("MongoDB no está disponible. No se pueden crear carros.")

    # Obtener el próximo ID
    max_cars = cars_collection.find().sort("cars_id", -1).limit(1)
    next_id = 1
    for car in max_cars:
        next_id = car["car_id"] + 1
        break

    new_car = {
            "car_id": next_id,
            "marca": car_data["marca"],
            "modelo": car_data["modelo"],
            "año": car_data["año"]
    }
    result = cars_collection.insert_one(new_car)
    new_car["_id"] = result.inserted_id
    return new_car, 201

@app.route('/new_user', methods=['POST'])
@admin_required
def create_new_user(user_data):
    """Agregar nuevo carro a MongoDB"""
    if db is None:
        raise Exception("MongoDB no está disponible. No se pueden crear carros.")

    # Obtener el próximo ID
    max_users = users_collection.find().sort("cars_id", -1).limit(1)
    next_id = 1
    for user in max_users:
        next_id = user["car_id"] + 1
        break
    new_user ={
            'id': next_id,
            'username': user_data["username"],
            'password_hash': generate_password_hash(user_data["password_hash"]),
            'role': user_data["role"],
            'created_at': user_data["created_at"]
    }
    result = users_collection.insert_one(new_user)
    new_user["_id"] = result.inserted_id
    return new_user, 201

@app.route('/cars/<int:car_id>/', methods=['DELETE'])
@admin_required
def delete_car(car_id):
    try:
        result = cars_collection.delete_one({'car_id': car_id})
        if result.deleted_count == 0:
            return "El carro no fue encontrado", 404
        return f"Se borró el carro con id: {car_id}", 200
    except Exception as e:
        return f"Error del servidor: {str(e)}", 500
    

############################# HTML-CSS- parte de MONGO ########################################

@app.route('/welcome', methods=['GET'])
def welcome_page():
    """Ejemplo de HTML con CSS"""
    html_content = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Bienvenida</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }
            
            body {
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%);
                color: white;
                overflow: hidden;
            }
            
            .container {
                max-width: 800px;
                width: 90%;
                text-align: center;
                padding: 40px;
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                border-radius: 20px;
                box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2);
                border: 1px solid rgba(255, 255, 255, 0.1);
                position: relative;
                z-index: 1;
            }
            
            .logo {
                width: 120px;
                height: 120px;
                margin: 0 auto 30px;
                background: rgba(255, 255, 255, 0.2);
                border-radius: 50%;
                display: flex;
                justify-content: center;
                align-items: center;
                font-size: 50px;
                box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
            }
            
            h1 {
                font-size: 3.5rem;
                margin-bottom: 20px;
                text-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
            }
            
            p {
                font-size: 1.2rem;
                line-height: 1.6;
                margin-bottom: 30px;
                opacity: 0.9;
            }
            
            .floating-elements {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                overflow: hidden;
                z-index: 0;
            }
            
            .floating-element {
                position: absolute;
                border-radius: 50%;
                background: rgba(255, 255, 255, 0.1);
            }
            
            .floating-element:nth-child(1) {
                width: 80px;
                height: 80px;
                top: 10%;
                left: 10%;
            }
            
            .floating-element:nth-child(2) {
                width: 100px;
                height: 100px;
                top: 70%;
                left: 80%;
            }
            
            .floating-element:nth-child(3) {
                width: 60px;
                height: 60px;
                top: 50%;
                left: 5%;
            }
            
            .floating-element:nth-child(4) {
                width: 120px;
                height: 120px;
                top: 20%;
                left: 85%;
            }
            
            .floating-element:nth-child(5) {
                width: 50px;
                height: 50px;
                top: 80%;
                left: 15%;
            }
            
            .highlight {
                background: #ff6b6b;
                color: white;
                padding: 5px 10px;
                border-radius: 20px;
                display: inline-block;
                margin: 10px 0;
            }
            
            @media (max-width: 768px) {
                h1 {
                    font-size: 2.5rem;
                }
                
                p {
                    font-size: 1rem;
                }
            }
        </style>
    </head>
    <body>
        <div class="floating-elements">
            <div class="floating-element"></div>
            <div class="floating-element"></div>
            <div class="floating-element"></div>
            <div class="floating-element"></div>
            <div class="floating-element"></div>
        </div>
        
        <div class="container">
            <div class="logo">🌟</div>
            <h1>¡Bienvenido!</h1>
            <p>Estamos encantados de tenerte aquí. Esta es una página de bienvenida moderna y elegante diseñada para crear una experiencia memorable desde el primer momento.</p>
            <div class="highlight">{{ current_time }}</div>
            <p>✨ MongoDB está <strong>{{ db_status }}</strong></p>
        </div>
    </body>
    </html>
    """
    db_status_value = "conectado" if db is not None else "desconectado"
    current_time_value = datetime.now().strftime("%H:%M:%S")
    
    return render_template_string(html_content,
                                db_status = db_status_value,
                                current_time = current_time_value)

@app.errorhandler(404)
def page_not_found():
    html_content_404 = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Página No Encontrada - Error 404</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }
            
            body {
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%);
                color: white;
                overflow: hidden;
            }
            
            .container {
                max-width: 800px;
                width: 90%;
                text-align: center;
                padding: 40px;
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                border-radius: 20px;
                box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2);
                border: 1px solid rgba(255, 255, 255, 0.1);
                position: relative;
                z-index: 1;
            }
            
            .error-code {
                font-size: 8rem;
                font-weight: bold;
                margin-bottom: 20px;
                text-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
                line-height: 1;
            }
            
            h1 {
                font-size: 2.5rem;
                margin-bottom: 20px;
                text-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
            }
            
            p {
                font-size: 1.2rem;
                line-height: 1.6;
                margin-bottom: 30px;
                opacity: 0.9;
            }
            
            .floating-elements {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                overflow: hidden;
                z-index: 0;
            }
            
            .floating-element {
                position: absolute;
                border-radius: 50%;
                background: rgba(255, 255, 255, 0.1);
            }
            
            .floating-element:nth-child(1) {
                width: 80px;
                height: 80px;
                top: 10%;
                left: 10%;
            }
            
            .floating-element:nth-child(2) {
                width: 100px;
                height: 100px;
                top: 70%;
                left: 80%;
            }
            
            .floating-element:nth-child(3) {
                width: 60px;
                height: 60px;
                top: 50%;
                left: 5%;
            }
            
            .floating-element:nth-child(4) {
                width: 120px;
                height: 120px;
                top: 20%;
                left: 85%;
            }
            
            .floating-element:nth-child(5) {
                width: 50px;
                height: 50px;
                top: 80%;
                left: 15%;
            }
            
            @media (max-width: 768px) {
                .error-code {
                    font-size: 6rem;
                }
                
                h1 {
                    font-size: 2rem;
                }
                
                p {
                    font-size: 1rem;
                }
            }
        </style>
    </head>
    <body>
        <div class="floating-elements">
            <div class="floating-element"></div>
            <div class="floating-element"></div>
            <div class="floating-element"></div>
            <div class="floating-element"></div>
            <div class="floating-element"></div>
        </div>
        
        <div class="container">
            <div class="error-code">404</div>
            <h1>Página No Encontrada</h1>
            <p>Lo sentimos, la página que estás buscando no existe o ha sido movida.</p>
        </div>
    </body>
    </html>
    """
    return render_template_string(html_content_404)


if __name__ == '__main__':
    initialize_users()
    initialize_cars()
    app.run(
        host='0.0.0.0',
        port=8003,
        debug=True
    )