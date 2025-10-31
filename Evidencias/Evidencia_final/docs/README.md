## Curl ejemplos con postman
# http://127.0.0.1:55056/welcome 
Esto te llevara a la pagina de welcome
# http://127.0.0.1:55056/car/id
Esto te mostrara el carro con esa id
# http://127.0.0.1:55056/car/id -> con el verbo POST
{
    "marca": "string",
    "modelo": "string",
    "año": "int"
}
Esto creara un nuevo carro

# http://127.0.0.1:55056/auth/login

# Con este body
{
    "username": "string",
    "password": "string"
}

Esto loguea a ese usuario (si existe)
