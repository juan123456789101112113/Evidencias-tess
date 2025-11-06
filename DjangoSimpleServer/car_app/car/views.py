from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Car
from .serializers import CarSerializer
from mongoengine.errors import DoesNotExist, ValidationError
from bson.errors import InvalidId


# ========== FUNCIONES AUXILIARES COMPARTIDAS ==========

def get_car_or_404(car_id):
    """
    Helper para obtener un carro o lanzar error 404
    
    Args:
        car_id (str): ID del carro
        
    Returns:
        Car: el carro encontrado
        
    Raises:
        DoesNotExist/InvalidId: Si el carro no existe
    """
    try:
        return Car.objects.get(id=car_id)
    except (DoesNotExist, InvalidId):
        # Retornar None si no existe (para que cada función maneje su error)
        return None


def validate_and_save_car(data, instance=None, partial=False):
    """
    Helper para validar y guardar un carro usando el serializer
    
    Args:
        data: Datos a validar
        instance: Instancia existente (para actualización) o None (para creación)
        partial: True para permitir actualizaciones parciales
        
    Returns:
        tuple: (serializer_data, error_response)
    """
    serializer = CarSerializer(instance, data=data, partial=partial)
    
    if serializer.is_valid():
        serializer.save()
        return serializer.data, None
    
    return None, Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def get_paginated_cars(limit=None, offset=None):
    """
    Helper para obtener carros con paginación opcional
    
    Args:
        limit: Número máximo de resultados
        offset: Número de resultados a saltar
        
    Returns:
        QuerySet: Carros filtrados
    """
    cars = Car.objects.all()
    
    if limit:
        limit = int(limit)
        offset = int(offset) if offset else 0
        cars = cars[offset:offset + limit]
    
    return cars


# ========== FUNCIONES DE LÓGICA DE NEGOCIO (Separadas por responsabilidad) ==========

def _handle_list_cars(request):
    """Lógica para listar todos los carros"""
    try:
        limit = request.query_params.get('limit')
        offset = request.query_params.get('offset')
        
        cars = get_paginated_cars(limit, offset)
        serializer = CarSerializer(cars, many=True)
        
        return Response({
            "count": Car.objects.count(),
            "results": serializer.data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {"error": f"Error al obtener los carros: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def _handle_create_car(request):
    """Lógica para crear un nuevo carro"""
    print(f"Creando carro: {request.data}")
    
    data, error = validate_and_save_car(request.data)
    
    if error:
        return error
    
    return Response(data, status=status.HTTP_201_CREATED)


def _handle_get_car(car_id):
    """Lógica para obtener un carro por ID"""
    car = get_car_or_404(car_id)
    
    if not car:
        return Response(
            {"error": f"No se encontró el carro con id: {car_id}"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer = CarSerializer(car)
    return Response(serializer.data, status=status.HTTP_200_OK)


def _handle_update_car(request, car_id):
    """Lógica para actualizar un carro"""
    print(f"Actualizando carro {car_id}: {request.data}")
    
    car = get_car_or_404(car_id)
    
    if not car:
        return Response(
            {"error": f"No se encontró una mesa con id: {car_id}"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # partial=True para PATCH, False para PUT
    partial = request.method == 'PATCH'
    data, error = validate_and_save_car(request.data, instance=car, partial=partial)
    
    if error:
        return error
    
    return Response(data, status=status.HTTP_200_OK)


def _handle_delete_car(car_id):
    """Lógica para eliminar una mesa"""
    car = get_car_or_404(car_id)
    
    if not car:
        return Response(
            {"error": f"No se encontró una mesa con id: {car_id}"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    car_name = car.marca
    car.delete()
    
    return Response(
        {
            "message": f"Carro '{car_name}' eliminado exitosamente",
            "car_id": car_id
        },
        status=status.HTTP_200_OK
    )


# ========== VISTAS (Dispatchers que delegan a funciones de lógica) ==========

@api_view(['GET', 'POST'])
def car_list(request):
    """
    GET  /api/car/  → Listar todos los carros
    POST /api/car/  → Crear un nuevo carro
    
    Esta vista actúa como dispatcher: Django enruta aquí por el path,
    y luego delegamos a la función específica según el método HTTP.
    """
    if request.method == 'GET':
        return _handle_list_cars(request)
    elif request.method == 'POST':
        return _handle_create_car(request)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def car_detail(request, car_id):
    """
    GET    /api/car/<id>  → Obtener un carro
    PUT    /api/car/<id>  → Actualizar carro completo
    PATCH  /api/car/<id>  → Actualizar carro parcialmente
    DELETE /api/car/<id>  → Eliminar carro
    
    Esta vista actúa como dispatcher: Django enruta aquí por el path,
    y luego delegamos a la función específica según el método HTTP.
    """
    if request.method == 'GET':
        return _handle_get_car(car_id)
    elif request.method in ['PUT', 'PATCH']:
        return _handle_update_car(request, car_id)
    elif request.method == 'DELETE':
        return _handle_delete_car(car_id)