from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
from bson import ObjectId

# Variables globales para la conexión
client = None
db = None
users_collection = None
cars_collection = None

def init_db(mongo_uri, database_name):
    """Inicializar conexión a MongoDB"""
    global client, db, users_collection, cars_collection
    
    try:
        client = MongoClient(mongo_uri)
        db = client[database_name]
        users_collection = db.users
        cars_collection = db.cars
        
        # Probar la conexión
        client.admin.command('ping')
        print("✅ Conexión a MongoDB exitosa")
        return True
    except Exception as e:
        print(f"❌ Error conectando a MongoDB: {e}")
        print("⚠️  La aplicación requiere MongoDB para funcionar correctamente.")
        client = None
        db = None
        return False

def get_db_status():
    """Obtener estado de la conexión a MongoDB"""
    return db is not None

# ========== FUNCIONES DE USUARIOS ==========

def initialize_users():
    """Inicializar usuarios en MongoDB si no existen"""
    if db is None:
        return
    
    # Verificar si ya existen usuarios
    if users_collection.count_documents({}) == 0:
        users_data = [
            {
                'user_id': 'user-2',
                'username': 'manager',
                'password_hash': generate_password_hash('manager123'),
                'role': 'manager',
                'created_at': datetime.now()
            },
            {
                'user_id': 'user-1',
                'username': 'admin1',
                'password_hash': generate_password_hash('admin123'),
                'role': 'admin',
                'created_at': datetime.now()
            }
        ]
        users_collection.insert_many(users_data)
        print("✅ Usuarios iniciales creados en MongoDB")

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

# ========== FUNCIONES DE CARROS ==========

def initialize_cars():
    """Inicializar carros en MongoDB si no existen"""
    if db is None:
        return
    
    # Verificar si ya existen carros
    if cars_collection.count_documents({}) == 0:
        cars_data = [
            {'id': 1, 'marca': 'Toyota', 'modelo': 'Corolla', 'año': 2020},
            {'id': 2, 'marca': 'Honda', 'modelo': 'Civic', 'año': 2019},
            {'id': 3, 'marca': 'Ford', 'modelo': 'Focus', 'año': 2018},
            {'id': 4, 'marca': 'Volkswagen', 'modelo': 'Golf', 'año': 2019},
            {'id': 5, 'marca': 'Chevrolet', 'modelo': 'Cruze', 'año': 2022}
        ]
        cars_collection.insert_many(cars_data)
        print("✅ carros iniciales creados en MongoDB")

def get_car_by_id(car_id):
    """Obtener carro por ID desde MongoDB"""
    if db is None:
        raise Exception("MongoDB no está disponible. No se pueden consultar carros.")
    
    return cars_collection.find_one({"car_id": int(car_id)})

def get_all_cars_filtered(marca_filter=None, modelo_filter=None):
    """Obtener todos los carros con filtros opcionales"""
    if db is None:
        raise Exception("MongoDB no está disponible. No se pueden consultar carros.")
    
    # Construir filtro para MongoDB
    filter_query = {}
    if marca_filter:
        filter_query["marca"] = {"$gte": int(marca_filter)}
    if modelo_filter:
        filter_query["modelo"] = {"$gte": int(modelo_filter)}
    
    return list(cars_collection.find(filter_query))

def add_new_car(car_data):
    """Agregar nuevo carro a MongoDB"""
    if db is None:
        raise Exception("MongoDB no está disponible. No se pueden crear carros.")
    
    # Obtener el próximo ID
    max_car = cars_collection.find().sort("car_id", -1).limit(1)
    next_id = 1
    for car in max_car:
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
    return new_car

def get_car_count():
    if db is None:
        return 0
    return cars_collection.count_documents({})

def get_all_cars():
    if db is None:
        return []
    return list(cars_collection.find({}))