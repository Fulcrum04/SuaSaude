from SuaSaude import db, app, login_manager
from datetime import datetime
from flask_login import UserMixin
import pandas as pd
import matplotlib.pyplot as plt


def table_to_dataframe(table):
    query = db.session.query(table).all()
    df = pd.DataFrame([item.__dict__ for item in query])
    df.drop('_sa_instance_state', axis=1, inplace=True)
    return df
    

def plot_exercise_pie_chart(exercise_condition, user_df):
    # Valores de porcentagens para cada categoria
    values = user_df['Exercise_Class'].value_counts(normalize=True) * 100
    
    # Explosão do gráfico para destacar a fatia correspondente ao exercício do usuário atual
    explode = [0.1 if label == exercise_condition else 0 for label in values.index]
    
    plt.figure(figsize=(10, 8))
    plt.pie(values, labels=values.index, autopct='%1.1f%%', explode=explode, textprops={'fontsize': 20})
    plt.savefig('SuaSaude/static/graficos/grafico_exercise.png', bbox_inches='tight')
    plt.close()


def plot_imc_pie_chart(imc_category, user_df):
    # Valores de porcentagens para cada categoria
    values = user_df['IMC_Class'].value_counts(normalize=True) * 100
    
    # Explosão do gráfico para destacar a fatia correspondente ao IMC do usuário atual
    explode = [0.1 if label == imc_category else 0 for label in values.index]
    
    plt.figure(figsize=(10, 8))
    plt.pie(values, labels=values.index, autopct='%1.1f%%', explode=explode, textprops={'fontsize': 20})
    plt.savefig('SuaSaude/static/graficos/grafico_imc.png', bbox_inches='tight')
    plt.close()


def classify_exercise(user):
    if user.idade < 18:
        if user.frequencia < 300:
            return 'Nenhuma'
        elif 300 <= user.frequencia <= 420:
            return 'Mínima'
        else:
            return 'Ideal'
    elif 18 <= user.idade <= 65:
        if user.frequencia < 150:
            return 'Nenhuma'
        elif 150 <= user.frequencia <= 300:
            return 'Mínima'
        else:
            return 'Ideal'
    else:  # idade > 65
        if user.frequencia < 75:
            return 'Nenhuma'
        elif 75 <= user.frequencia <= 150:
            return 'Mínima'
        else:
            return 'Ideal'


def classify_imc(user):
    if user.IMC < 18.5:
        return 'Baixo Peso'
    elif 18.5 <= user.IMC < 24.9:
        return 'Peso Normal'
    elif 24.9 <= user.IMC < 29.9:
        return 'Sobrepeso'
    else:
        return 'Obesidade'


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
