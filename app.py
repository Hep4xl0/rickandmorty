from flask_sqlalchemy import SQLAlchemy
from flask import Flask, jsonify, render_template
import requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123123@localhost:3306/rick'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Character(db.Model):
    __tablename__ = 'personagens'
    id = db.Column(db.Integer, primary_key=True)  
    nome = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(50))
    species = db.Column(db.String(50)) 
    gender = db.Column(db.String(20)) 
    location = db.Column(db.String(100))  
    imagem = db.Column(db.String(255))  
    episodios = db.Column(db.Integer) 
    
    def __repr__(self):
        return f'<Character {self.nome}>'



def get(page=1):
    url = f'https://rickandmortyapi.com/api/character?page={page}'
    resposta = requests.get(url)
    return resposta.json()



def armazenar(data):
    for personagem in data['results']:
        novo = Character(
            id=personagem['id'],
            nome=personagem['name'],
            status=personagem['status'],
            species=personagem['species'],
            gender=personagem['gender'],
            location=personagem['location']['name'], 
            imagem=personagem['image'],
            episodios=len(personagem['episode']),
        )
        db.session.add(novo)
    db.session.commit()

@app.route('/', methods=['GET'])
def guardar():
    data_inicio = get(1)
    
    
    total_pages = data_inicio['info']['pages']
    armazenar(data_inicio)

    for page in range(2, total_pages + 1):
        data = get(page)
        if data:
            armazenar(data)

    return jsonify({"message": "Dados inseridos com sucesso!"}), 200

@app.route('/personagens', methods=['GET'])
def mostrar():
    personagens = Character.query.all()
    return render_template('index.html', personagens=personagens)

if __name__ == '__main__':
    app.run()
