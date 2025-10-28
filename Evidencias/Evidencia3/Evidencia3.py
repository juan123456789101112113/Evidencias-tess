from flask import Flask, request

app = Flask(__name__)

carros = [
    {'id': 1, 'marca': 'Toyota', 'modelo': 'Corolla', 'año': 2020},
    {'id': 2, 'marca': 'Honda', 'modelo': 'Civic', 'año': 2019},
    {'id': 3, 'marca': 'Ford', 'modelo': 'Focus', 'año': 2018},
    {'id': 4, 'marca': 'Volkswagen', 'modelo': 'Golf', 'año': 2019},
    {'id': 5, 'marca': 'Chevrolet', 'modelo': 'Cruze', 'año': 2022}
]

@app.route('/carros/', methods=['GET'])
def filter_carros():
    marca_query_param = request.args.get("marca")
    modelo_query_param = request.args.get("modelo")
    print(f"marca {marca_query_param}, modelo {modelo_query_param}")
    ans = carros
    if marca_query_param is not None:
        ans = list(filter(lambda x: x ["marca"] == marca_query_param, ans))
    if modelo_query_param is not None:
        ans = list(filter(lambda x: x ["modelo"] == modelo_query_param, ans))
    return ans, 200

@app.route('/carros/<string:carro_id>/', methods=['GET'])
def get_carro(carro_id):
    ans = list(filter(lambda x: x ["id"] == int(carro_id), carros))
    if len(ans) > 0:
        return ans[0], 200
    else:
        return {"mensaje": "Carro no existe"}, 404

@app.route('/carros/', methods=['POST'])
def post_carro():
    print(f"body: {request.json}")
    body = request.json
    new_carro ={
            "id": body["id"],
            "marca": body["marca"],
            "modelo": body["modelo"],
            "año": body["año"],
    }
    carros.append(new_carro)
    return new_carro, 201

@app.route('/carros/<string:carro_id>/', methods=['DELETE'])
def delete_carro(carro_id):
    global carros
    carros = list(filter(lambda x: x["id"] != int(carro_id), carros))
    return f"se borro el carro de id: {carro_id}", 204


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=8003,
        debug=True
    )