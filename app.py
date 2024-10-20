from flask_sqlalchemy import SQLAlchemy
from flask import Flask, jsonify
import requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123123@localhost:3306/rick'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Definição do modelo da tabela 'personagens'
class Character(db.Model):
    __tablename__ = 'personagens'  # Nome da tabela no banco de dados
    
    # Definindo as colunas
    id = db.Column(db.Integer, primary_key=True)  # ID único do personagem
    nome = db.Column(db.String(100), nullable=False)  # Nome do personagem, obrigatório
    status = db.Column(db.String(50))  # Status (Alive, Dead, Unknown)
    species = db.Column(db.String(50))  # Espécie (Human, Alien, etc.)
    gender = db.Column(db.String(20))  # Gênero (Male, Female, etc.)
    location = db.Column(db.String(100))  # Última localização conhecida
    imagem = db.Column(db.String(255))  # URL da imagem/avatar
    episodios = db.Column(db.Integer)  # Quantidade de episódios em que apareceu
    
    def __repr__(self):
        return f'<Character {self.nome}>'

# Criar as tabelas se ainda não existirem
with app.app_context():
    db.create_all()

# Função para buscar os dados de uma página específica da API
def get_data_from_api(page=1):
    url = f'https://rickandmortyapi.com/api/character?page={page}'
    resposta = requests.get(url)
    if resposta.status_code == 200:
        return resposta.json()
    return None

# Função para armazenar os dados no banco de dados
def armazenar(data):
    for personagem in data['results']:
        novo = Character(
            id=personagem['id'],
            nome=personagem['name'],
            status=personagem['status'],
            species=personagem['species'],
            gender=personagem['gender'],
            location=personagem['location']['name'],  # Acessando 'name' dentro de 'location'
            imagem=personagem['image'],  # URL da imagem
            episodios=len(personagem['episode']),  # Contando quantos episódios
        )
        db.session.add(novo)
    db.session.commit()

# Rota para buscar e armazenar os personagens da API
@app.route('/', methods=['GET'])
def guardar():
    data_inicio = get_data_from_api(1)  # Pegando a primeira página
    
    
    total_pages = data_inicio['info']['pages']  # Quantidade total de páginas
    armazenar(data_inicio)  # Armazenando a primeira página

    # Loop para pegar as páginas seguintes e armazenar os dados
    for page in range(2, total_pages + 1):
        data = get_data_from_api(page)
        if data:
            armazenar(data)

    return jsonify({"message": "Dados inseridos com sucesso!"}), 200

# Rodar a aplicação Flask
if __name__ == '__main__':
    app.run()
