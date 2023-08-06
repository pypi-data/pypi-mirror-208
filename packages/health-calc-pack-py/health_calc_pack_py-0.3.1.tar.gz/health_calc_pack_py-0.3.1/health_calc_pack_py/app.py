from flask import Flask, request, jsonify
from flask_swagger_ui import get_swaggerui_blueprint

from .imc import calcular_imc
from .macronutrientes import calcular_macronutrientes, OBJETIVOS

app = Flask(__name__)

SWAGGER_URL = "/docs"
API_URL = "/static/swagger.json"

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        "app_name": "Health Calc Pack Py"
    }
)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

@app.route('/calcular_imc', methods=['POST'])
def imc():
    data = request.get_json()

    if not data:
        return jsonify({"erro": "JSON inválido"}), 400

    peso = data.get('peso')
    altura = data.get('altura')

    if peso is None or altura is None:
        return jsonify({"erro": "Os campos 'peso' e 'altura' são obrigatórios"}), 400

    try:
        peso = float(peso)
        altura = float(altura)
    except ValueError:
        return jsonify({"erro": "Os campos 'peso' e 'altura' devem ser numéricos"}), 400

    if peso <= 0 or altura <= 0:
        return jsonify({"erro": "Os campos 'peso' e 'altura' devem ser maiores que zero"}), 400

    imc = calcular_imc(peso, altura)

    return jsonify({"IMC": imc})

@app.route('/calcular_macronutrientes', methods=['POST'])
def macronutrientes():
    data = request.get_json()

    if not data:
        return jsonify({"erro": "JSON inválido"}), 400

    peso = data.get('peso')
    objetivo = data.get('objetivo')

    if peso is None or objetivo is None:
        return jsonify({"erro": "Os campos 'peso' e 'objetivo' são obrigatórios"}), 400

    try:
        peso = float(peso)
    except ValueError:
        return jsonify({"erro": "O campo 'peso' deve ser numérico"}), 400

    if peso <= 0:
        return jsonify({"erro": "O campo 'peso' deve ser maior que zero"}), 400

    try:
        resultado = calcular_macronutrientes(peso, objetivo)
    except ValueError:
        return jsonify({"erro": "Objetivo inválido. Os objetivos válidos são:", "objetivos": OBJETIVOS}), 400

    return jsonify(resultado)

if __name__ == '__main__':
    app.run(debug=True)
