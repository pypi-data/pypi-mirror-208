# Health Calc Pack Py

Health Calc Pack Py é uma API para calcular o Índice de Massa Corporal (IMC) e os macronutrientes necessários para um indivíduo de acordo com seu objetivo nutricional.

## Instalação

1. Clone o repositório:
git clone https://github.com/Angelo-Diniz/health-calc-pack-py

2. Entre no diretório do projeto:

cd health_calc_pack_py

3. Crie um ambiente virtual e ative-o (opcional, mas recomendado):

python -m venv venv

source venv/bin/activate  # Linux/macOS

venv\Scripts\activate  # Windows

4. Entre na diretorio /health_calc_pack_py

5. Instale as dependências:

poetry install

Obs: Certifique-se de que o Poetry esteja instalado. Caso contrário, instale-o seguindo as instruções na documentação oficial: https://python-poetry.org/docs/#installation

## Executando localmente

Após instalar as dependências, execute o seguinte comando para iniciar o servidor de desenvolvimento:

poetry run python -m health_calc_pack_py.app

A API estará disponível em http://localhost:5000. Envie requisições HTTP para os endpoints disponíveis para interagir com a aplicação.

## Swagger
Acesse o http://localhost:5000/docs/

## Testes unitários

python -m unittest discover tests

Isso executará todos os testes unitários definidos na pasta tests e exibirá os resultados.

## Testes unitários

Endpoints

A API fornece os seguintes endpoints:

/imc: Recebe um JSON contendo altura e peso, e retorna o IMC calculado.

/macronutrientes: Recebe um JSON contendo peso e objetivo nutricional, e retorna os macronutrientes calculados.
