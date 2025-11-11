from mongoengine import Document, StringField, IntField

# Modelo del carro usando MongoEngine
class Car(Document):
    """
    Modelo para representar un carro en MongoDB
    """
    marca = StringField(required=True, max_length=100)
    modelo = StringField(required=True, max_length=100)
    año = IntField(required=True, min_value=0)
    
    meta = {
        'collection': 'cars',  # Nombre de la colección en MongoDB
        'ordering': ['marca']     # Ordenar por nombre por defecto
    }
    
    def to_dict(self):
        """
        Convierte el documento de MongoDB a un diccionario para la API
        """
        return {
            'car_id': str(self.id),  # MongoDB usa ObjectId, lo convertimos a string
            'marca': self.marca,
            'modelo': self.modelo,
            'año': self.año
        }