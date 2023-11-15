from flask import render_template, redirect, url_for, flash, request, abort
from comunidade.forms import FormCriarConta, FormLogin, FormEditarPerfil, FormCriarPost
from comunidade import app, db, bcrypt, login_manager
from comunidade.models import Usuario, Post
from flask_login import login_user, logout_user, current_user, login_required
import secrets
import os
from PIL import Image


@app.route('/')
def home():
    posts = Post.query.all()
    return render_template('home.html', posts=posts)


@app.route('/contato')
def contato():
    return render_template('contato.html')


@app.route('/usuarios')
@login_required
def usuarios():
    lista_usuarios = Usuario.query.all()
    return render_template('usuarios.html', lista_usuarios=lista_usuarios)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form_login = FormLogin()

    if form_login.validate_on_submit():
        # flash(f'Bem-vindo(a), {}')
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
            db.session.add(usuario)
            db.session.commit()
        # flash(f'Bem-vindo(a), {}')
        flash(f'Conta criada com sucesso para o E-mail {form_criarconta.email.data}', 'alert-success')
        return redirect(url_for('home'))

    return render_template('criar_conta.html', form_criarconta=form_criarconta)


@app.route('/sair')
@login_required
def sair():
    logout_user()
    flash('Logout feito com sucesso!', 'alert-success')
    return redirect(url_for('home'))


@app.route('/post/criar', methods=['GET', 'POST'])
@login_required
def criar_post():
    form = FormCriarPost()
    if form.validate_on_submit():
        post = Post(titulo=form.titulo.data, corpo=form.corpo.data, autor=current_user)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('criar_post.html', form=form)


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
        if form.foto_perfil.data:
            nome_imagem = salvar_imagem(form.foto_perfil.data)
            current_user.foto_perfil = nome_imagem
        flash('Perfil atualizado com sucesso!', 'alert-success')
        db.session.commit()
        return redirect(url_for('perfil'))
    elif request.method == 'GET':
        form.email.data = current_user.email
        form.username.data = current_user.username
        form.idade.data = current_user.idade
    return render_template('editar_perfil.html', foto_perfil=foto_perfil, form=form)


@app.route('/post/<post_id>', methods=['GET', 'POST'])
@login_required
def exibir_post(post_id):
    post = Post.query.get(post_id)
    if current_user == post.autor:
        form = FormCriarPost()
        if request.method == 'GET':
            form.corpo.data = post.corpo
            form.titulo.data = post.titulo
        elif form.validate_on_submit():
            post.titulo = form.titulo.data
            post.corpo = form.corpo.data
            db.session.commit()
            flash('Post atualizado com sucesso!', 'alert-success')
            return redirect(url_for('home'))
        return render_template('exibir_post.html', post=post, form=form)
    return render_template('exibir_post.html', post=post)

@app.route('/post/<post_id>/excluir', methods=['GET', 'POST'])
@login_required
def excluir_post(post_id):
    post = Post.query.get(post_id)
    if current_user == post.autor:
        db.session.delete(post)
        db.session.commit()
        flash('Post excluído com sucesso!', 'alert-danger')
        return redirect(url_for('home'))
    else:
        abort(403)


