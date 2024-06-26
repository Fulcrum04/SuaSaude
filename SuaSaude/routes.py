from flask import render_template, redirect, url_for, flash, request, abort
from SuaSaude.forms import FormCriarConta, FormLogin, FormEditarPerfil
from SuaSaude import app, db, bcrypt, login_manager
from SuaSaude.models import Usuario, Links, table_to_dataframe, classificar_usuario
from flask_login import login_user, logout_user, current_user, login_required
import secrets
import os
from PIL import Image
import pandas as pd
import matplotlib.pyplot as plt


@app.route('/')
def home():
    if current_user.is_authenticated:
        tipo, posts, faixa_etaria, frequencia_minima, frequencia_ideal = classificar_usuario(current_user)
        return render_template('home_log.html', posts=posts, tipo=tipo, faixa_etaria=faixa_etaria,
                               frequencia_ideal=frequencia_ideal, frequencia_minima=frequencia_minima)
    else:
        return render_template("home.html")


@app.route('/contato')
def contato():
    return render_template('contato.html')


@app.route('/dados')
@login_required
def dados():
    tipo, posts, faixa_etaria, frequencia_minima, frequencia_ideal = classificar_usuario(current_user)
    
    explode_imc = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    explode_imc[tipo - 1] = 0.1

    explode_exercise = [0.0, 0.0, 0.0]
    if frequencia_minima > current_user.frequencia:
        index_a_substituir = 0
    elif frequencia_minima <= current_user.frequencia < frequencia_ideal:
        index_a_substituir = 1
    else:
        index_a_substituir = 2
    explode_exercise[index_a_substituir] = 0.1
    
    user_df = table_to_dataframe(Usuario)
    conditions_imc = [
        (user_df['IMC'] < 18.6),
        (user_df['IMC'] >= 18.6) & (user_df['IMC'] < 25),
        (user_df['IMC'] >= 25) & (user_df['IMC'] < 30),
        (user_df['IMC'] >= 30) & (user_df['IMC'] < 35),
        (user_df['IMC'] >= 35) & (user_df['IMC'] < 40),
        (user_df['IMC'] >= 40)
    ]
    choices_imc = ['Abaixo do Peso', 'Peso Ideal', 'Acima do Peso', 'Obesidade I', 'Obesidade II', 'Obesidade III']
    user_df['IMC_Class'] = pd.cut(user_df['IMC'], bins=[-float('inf'), 18.6, 25, 30, 35, 40, float('inf')],
                                  labels=choices_imc)

    # Contagem das classificações de IMC
    imc_counts = user_df['IMC_Class'].value_counts().reindex(choices_imc, fill_value=0).reset_index()
    imc_counts.columns = ['index', 'quantidade']

    # Classificações de Frequência de Exercício
    def classify_exercise(row):
        if row['idade'] < 18:
            if row['frequencia'] < 300:
                return 'Nenhuma'
            elif 300 <= row['frequencia'] <= 420:
                return 'Mínima'
            else:
                return 'Ideal'
        elif 18 <= row['idade'] <= 65:
            if row['frequencia'] < 150:
                return 'Nenhuma'
            elif 150 <= row['frequencia'] <= 300:
                return 'Mínima'
            else:
                return 'Ideal'
        else:  # idade > 65
            if row['frequencia'] < 75:
                return 'Nenhuma'
            elif 75 <= row['frequencia'] <= 150:
                return 'Mínima'
            else:
                return 'Ideal'

    user_df['Exercise_Class'] = user_df.apply(classify_exercise, axis=1)

    # Contagem das classificações de frequência de exercício
    exercise_counts = user_df['Exercise_Class'].value_counts().reindex(
        ['Nenhuma', 'Mínima', 'Ideal'], fill_value=0).reset_index()
    exercise_counts.columns = ['index', 'quantidade']

    # Criação e salvamento dos gráficos de pizza
    graficos_path = 'SuaSaude/static/graficos'
    os.makedirs(graficos_path, exist_ok=True)

    def create_pie_chart(data, file_path, explode_list):
        plt.figure(figsize=(10, 8))
        plt.pie(data['quantidade'], labels=data['index'], autopct='%1.1f%%', startangle=140, explode=explode_list, textprops={'fontsize': 20})
        plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        plt.savefig(file_path)
        plt.close()

    try:
        create_pie_chart(imc_counts, os.path.join(graficos_path, 'grafico_imc.png'), explode_imc)
        create_pie_chart(exercise_counts, os.path.join(graficos_path, 'grafico_exercise.png'), explode_exercise)
        print("Gráficos salvos com sucesso.")
    except Exception as e:
        print(f"Erro ao salvar gráficos: {e}")

    return render_template('dados.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form_login = FormLogin()

    if form_login.validate_on_submit():
        usuario = Usuario.query.filter_by(email=form_login.email.data).first()
        if usuario and bcrypt.check_password_hash(usuario.senha.encode('utf-8'), form_login.senha.data):
            flash(f'Login feito com sucesso para o E-mail {form_login.email.data}', 'alert-success')
            login_user(usuario, remember=form_login.lembrar_dados.data)
            par_next = request.args.get('next')
            if par_next:
                return redirect(par_next)
            else:
                return redirect(url_for('home'))
        else:
            flash("Falha no login! Email ou senha incorretos.", 'alert-danger')

    return render_template('login.html', form_login=form_login)


@app.route('/criar_conta', methods=['GET', 'POST'])
def criar_conta():
    form_criarconta = FormCriarConta()

    if form_criarconta.validate_on_submit():
        with app.app_context():
            senha = bcrypt.generate_password_hash(form_criarconta.senha.data).decode('utf-8')
            usuario = Usuario(username=form_criarconta.username.data, email=form_criarconta.email.data, senha=senha,
                              idade=form_criarconta.idade.data, altura=form_criarconta.altura.data,
                              peso=form_criarconta.peso.data, frequencia=form_criarconta.frequencia.data)
            usuario.calc_IMC()
            db.session.add(usuario)
            db.session.commit()
        # flash(f'Bem-vindo(a), {}')
        flash(f'Conta criada com sucesso para o E-mail {form_criarconta.email.data}', 'alert-success')
        usuario = Usuario.query.filter_by(email=form_criarconta.email.data).first()
        login_user(usuario, remember=True)
        return redirect(url_for('home'))

    return render_template('criar_conta.html', form_criarconta=form_criarconta)


@app.route('/sair')
@login_required
def sair():
    logout_user()
    flash('Logout feito com sucesso!', 'alert-success')
    return redirect(url_for('home'))


@app.route('/perfil')
@login_required
def perfil():
    foto_perfil = url_for('static', filename='fotos_perfil/{}'.format(current_user.foto_perfil))
    return render_template('perfil.html', foto_perfil=foto_perfil)


def salvar_imagem(foto):
    codigo = secrets.token_hex(8)
    nome, extensao = os.path.splitext(foto.filename)
    nome_arquivo = nome + codigo + extensao
    caminho = os.path.join(app.root_path, 'static/fotos_perfil', nome_arquivo)
    tamanho = (200,200)
    imagem_reduzida = Image.open(foto)
    imagem_reduzida.thumbnail(tamanho)
    imagem_reduzida.save(caminho)

    return nome_arquivo


@app.route('/perfil/editar', methods=['GET', 'POST'])
@login_required
def editar_perfil():
    foto_perfil = url_for('static', filename='fotos_perfil/{}'.format(current_user.foto_perfil))
    form = FormEditarPerfil()
    if form.validate_on_submit():
        current_user.email = form.email.data
        current_user.username = form.username.data
        current_user.idade = form.idade.data
        current_user.altura = form.altura.data
        current_user.peso = form.peso.data
        current_user.frequencia = form.frequencia.data
        if form.foto_perfil.data:
            nome_imagem = salvar_imagem(form.foto_perfil.data)
            current_user.foto_perfil = nome_imagem
        flash('Perfil atualizado com sucesso!', 'alert-success')
        current_user.calc_IMC()
        db.session.commit()
        return redirect(url_for('perfil'))
    elif request.method == 'GET':
        form.email.data = current_user.email
        form.username.data = current_user.username
        form.idade.data = current_user.idade
        form.altura.data = current_user.altura
        form.peso.data = current_user.peso
        form.frequencia.data = current_user.frequencia

    return render_template('editar_perfil.html', foto_perfil=foto_perfil, form=form)
