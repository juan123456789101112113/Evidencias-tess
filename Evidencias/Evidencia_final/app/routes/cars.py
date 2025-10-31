from flask import Blueprint, request, jsonify
from app.models import get_car_by_id, get_all_cars_filtered, add_new_car
from app.utils import role_required, admin_required

car_bp = Blueprint('car', __name__)

@car_bp.route('/<string:car_id>/', methods=["GET"])
@role_required
def get_car(car_id):
    """Obtener escritorio por ID"""
    try:
        car = get_car_by_id(car_id)
        if car:
            # Normalizar la respuesta para mantener compatibilidad
            if '_id' in car:
                del car['_id']  # Remover ObjectId de MongoDB
            if 'car_id' in car:
                car['id'] = car['car_id']  # Mantener compatibilidad con 'id'
            return car, 200
        else:
            print("ERROR")
            return {"mensaje": "Mesa no existe"}, 404
    except Exception as e:
        return jsonify({
            'error': 'Error de base de datos',
            'message': 'No se puede conectar a la base de datos. Verifique que MongoDB esté ejecutándose.'
        }), 503

@car_bp.route('', methods=["GET"])
@role_required
def get_all_cars():
    """Obtener todos los escritorios con filtros opcionales"""
    width_query_param = request.args.get("width")
    height_query_param = request.args.get("height")
    print(f"width {width_query_param}, height {height_query_param}")
    
    try:
        cars = get_all_cars_filtered(width_query_param, height_query_param)
        
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
            'message': 'No se puede conectar a la base de datos. Verifique que MongoDB esté ejecutándose.'
        }), 503

@car_bp.route('', methods=["POST"])
@admin_required
def post_car():
    """Crear nuevo escritorio (solo administradores)"""
    print(f"Body: {request.json}")
    body = request.json
    
    # Validar datos requeridos
    if not all(key in body for key in ['name', 'width', 'height']):
        return jsonify({
            'error': 'Datos incompletos',
            'message': 'Se requieren name, width y height'
        }), 400
    
    try:
        new_car_data = {
            "name": body["name"],
            "width": body["width"],
            "height": body["height"]
        }
        
        new_car = add_new_car(new_car_data)
        
        # Normalizar respuesta
        if '_id' in new_car:
            del new_car['_id']
        if 'car_id' in new_car:
            new_car['id'] = new_car['car_id']
        
        return new_car, 201
    except Exception as e:
        return jsonify({
            'error': 'Error de base de datos',
            'message': 'No se puede conectar a la base de datos. Verifique que MongoDB esté ejecutándose.'
        }), 503