from rest_framework import serializers
from .models import Car


class CarSerializer(serializers.Serializer):
    """
    Serializer para el modelo Car de MongoDB
    Maneja la validación automática de campos
    """
    car_id = serializers.SerializerMethodField(read_only=True)
    marca = serializers.CharField(required=True, max_length=100)
    modelo = serializers.CharField(required=True, max_length=100)
    año = serializers.IntegerField(required=True, min_value=0)
    
    def create(self, validated_data):
        """
        Crea un nuevo carro con los datos validados
        """
        car = Car(**validated_data)
        car.save()
        return car
    
    def update(self, instance, validated_data):
        """
        Actualiza un carro existente con los datos validados
        """
        instance.marca = validated_data.get('marca', instance.marca)
        instance.modelo = validated_data.get('modelo', instance.modelo)
        instance.año = validated_data.get('año', instance.año)
        instance.save()
        return instance
    
    def to_representation(self, instance):
        """
        Convierte el objeto Car a diccionario
        """
        return {
            'car_id': str(instance.id),
            'marca': instance.marca,
            'modelo': instance.modelo,
            'año': instance.año
        }