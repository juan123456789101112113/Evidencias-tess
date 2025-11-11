from django.shortcuts import render
from car.models import Car

# Create your views here.

cars = [
        {'car_id': 1, 'marca': 'Toyota', 'modelo': 'Corolla', 'año': 2020},
        {'car_id': 2, 'marca': 'Honda', 'modelo': 'Civic', 'año': 2019},
        {'car_id': 3, 'marca': 'Ford', 'modelo': 'Focus', 'año': 2018},
        {'car_id': 4, 'marca': 'Volkswagen', 'modelo': 'Golf', 'año': 2019},
        {'car_id': 5, 'marca': 'Chevrolet', 'modelo': 'Cruze', 'año': 2022}
]

def get_car(_,car_id):
        filtered = list(filter(lambda x : x["car_id"]==car_id,cars))
        return filtered[0]


def get_cars(request):
        cars_from_db = Car.objects.all()
        contexto = {
        "cars" : cars_from_db,
        "tab_title": "GET ALL CARS"
        }
        return render(request,'dynamic_templates/car_list.html', contexto)