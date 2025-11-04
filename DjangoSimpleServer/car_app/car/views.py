from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Create your views here.

@api_view('GET')
def get_car(_):
    return Response({"id": 1, "marca": "Toyota", "modelo": "Corolla", "año": 2020})