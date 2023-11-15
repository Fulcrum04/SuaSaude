from comunidade import db, app, login_manager
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
        posts = db.relationship('Post', backref='autor', lazy=True)
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


    class Post(db.Model):
        __tablename__ = 'Post'
        id = db.Column(db.Integer, primary_key=True)
        titulo = db.Column(db.String, nullable=False)
        corpo = db.Column(db.Text, nullable=False)
        data_criacao = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
        id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)

    db.create_all()
