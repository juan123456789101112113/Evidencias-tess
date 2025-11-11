from django.urls import path
from . import views

urlpatterns = [
    path('car/<str:car_id>', views.get_car, name='template_get_car'),
    path('', views.get_cars,  name='template_get_all_cars')
]