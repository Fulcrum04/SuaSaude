from SuaSaude import db, app, login_manager
from datetime import datetime
from flask_login import UserMixin
import pandas as pd


def classificar_usuario(current_user):
    #filtrar posts de acordo com o IMC do usuário
    if current_user.IMC < 18.6:
        tipo = 1
        posts = Links.query.filter_by(tipo=tipo)
    elif current_user.IMC < 25:
        tipo = 2
        posts = Links.query.filter_by(tipo=tipo)
    elif current_user.IMC < 30:
        tipo = 3
        posts = Links.query.filter_by(tipo=tipo)
    elif current_user.IMC < 35:
        tipo = 4
        posts = Links.query.filter_by(tipo=tipo)
    elif current_user.IMC < 40:
        tipo = 5
        posts = Links.query.filter_by(tipo=tipo)
    else:
        tipo = 6
        posts = Links.query.filter_by(tipo=tipo)
    if current_user.idade < 18:
        faixa_etaria = 1
        frequencia_minima = 300
        frequencia_ideal = 420
    elif current_user.idade < 64:
        faixa_etaria = 2
        frequencia_minima = 150
        frequencia_ideal = 300
    else:
        faixa_etaria = 3
        frequencia_minima = 75
        frequencia_ideal = 150
    return tipo, posts, faixa_etaria, frequencia_minima, frequencia_ideal


def table_to_dataframe(table):
    query = db.session.query(table).all()
    df = pd.DataFrame([item.__dict__ for item in query])
    df.drop('_sa_instance_state', axis=1, inplace=True)
    return df


@login_manager.user_loader
def load_usuario(id_usuario):
    return Usuario.query.get(int(id_usuario))


with app.app_context():

    class Usuario(db.Model, UserMixin):
        __tablename__ = 'usuario'
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String, nullable=False)
        senha = db.Column(db.String, nullable=False)
        email = db.Column(db.String, nullable=False, unique=True)
        foto_perfil = db.Column(db.String, nullable=False, default='default.jpg')
        idade = db.Column(db.Integer)
        peso = db.Column(db.Float)
        altura = db.Column(db.Float)
        frequencia = db.Column(db.Integer)
        IMC = db.Column(db.Float)

        def contar_posts(self):
            len(self.posts)

        def calc_IMC(self):
            imc = self.peso / self.altura ** 2
            self.IMC = imc


    class Links(db.Model):
        __tablename__ = 'Links'
        id = db.Column(db.Integer, primary_key=True)
        titulo = db.Column(db.String, nullable=False)
        address = db.Column(db.String)
        tipo = db.Column(db.Integer, nullable=False)

    db.create_all()
