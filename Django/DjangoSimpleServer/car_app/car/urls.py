from django.urls import path
from . import views

"""
URLs RESTful para el API de caros:

⚠️ IMPORTANTE: Django NO diferencia por método HTTP en el routing.
   Solo importa el PATRÓN de la URL.
   Por eso usamos SOLO 2 paths, y cada vista maneja múltiples métodos HTTP.

Funcionamiento:
1. Django recibe una request (ej: GET /api/car/123)
2. Compara con los patterns en orden
3. Encuentra el primer match (ej: '<str:car_id>')
4. Llama a esa vista (ej: views.car_detail)
5. La vista mira request.method y delega a la función correcta

GET    /api/car/        → car_list()   → _handle_list_cars()
POST   /api/car/        → car_list()   → _handle_create_car()
GET    /api/car/<id>    → car_detail() → _handle_get_car()
PUT    /api/car/<id>    → car_detail() → _handle_update_car()
PATCH  /api/car/<id>    → car_detail() → _handle_update_car()
DELETE /api/car/<id>    → car_detail() → _handle_delete_car()
"""

urlpatterns = [
    # Colección: /api/car/
    # car_list maneja GET (listar) y POST (crear)
    path('', views.car_list, name='car_list'),
    
    # Recurso individual: /api/car/<id>
    # car_detail maneja GET, PUT, PATCH y DELETE
    path('<str:car_id>', views.car_detail, name='car_detail'),
    
    # Endpoint para imágenes: /api/car/items/?img=<nombre_imagen>
    path('items/', views.items_list, name='items_list'),
]