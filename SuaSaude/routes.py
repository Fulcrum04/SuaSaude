from flask import render_template, redirect, url_for, flash, request, abort
from SuaSaude.forms import FormCriarConta, FormLogin, FormEditarPerfil
from SuaSaude import app, db, bcrypt, login_manager
from SuaSaude.models import Usuario, Links, table_to_dataframe, classify_exercise, classify_imc, plot_exercise_pie_chart, plot_imc_pie_chart
from flask_login import login_user, logout_user, current_user, login_required
import secrets
import os
from PIL import Image
import pandas as pd


@app.route('/')
def home():
    if current_user.is_authenticated:
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
        return render_template('home_log.html', posts=posts, tipo=tipo, faixa_etaria=faixa_etaria,
                               frequencia_ideal=frequencia_ideal, frequencia_minima=frequencia_minima)
    else:
        return render_template("home.html")


@app.route('/contato')
def contato():
    return render_template('contato.html')


@app.route('/dados')
def dados():
    user_df = table_to_dataframe(Usuario)
    user_df['Exercise_Class'] = user_df.apply(lambda row: classify_exercise(row), axis=1)
    exercise_condition = classify_exercise(current_user)
    imc_category = classify_imc(current_user)
    
    plot_exercise_pie_chart(exercise_condition, user_df)
    plot_imc_pie_chart(imc_category, user_df)

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
