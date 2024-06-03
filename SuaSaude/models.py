from SuaSaude import db, app, login_manager
from datetime import datetime
from flask_login import UserMixin


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
