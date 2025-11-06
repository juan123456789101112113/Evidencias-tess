from django.shortcuts import render

# Create your views here.

cars = [
        {'id': 1, 'marca': 'Toyota', 'modelo': 'Corolla', 'año': 2020},
        {'id': 2, 'marca': 'Honda', 'modelo': 'Civic', 'año': 2019},
        {'id': 3, 'marca': 'Ford', 'modelo': 'Focus', 'año': 2018},
        {'id': 4, 'marca': 'Volkswagen', 'modelo': 'Golf', 'año': 2019},
        {'id': 5, 'marca': 'Chevrolet', 'modelo': 'Cruze', 'año': 2022}
]

def get_car(_,car_id):
        filtered = list(filter(lambda x : x["car_id"]==car_id,cars))
        return filter[0]


def get_cars(request):
        contexto = {
        "cars" : cars,
        "tab_title": "GET ALL CARS"
        }
        return render(request,'dynamic_templates/car_list.html', contexto)