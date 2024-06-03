from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import StringField, SubmitField, PasswordField, BooleanField, TextAreaField, IntegerField, FloatField
from wtforms.validators import Email, DataRequired, EqualTo, Length, ValidationError
from SuaSaude.models import Usuario
from flask_login import current_user


class FormCriarConta(FlaskForm):
    username = StringField('Nome de Usuário', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    senha = PasswordField('Senha', validators=[DataRequired(), Length(6, 20)])
    confirmacao_senha = PasswordField('Confirmação da Senha', validators=[DataRequired(), EqualTo('senha')])
    idade = IntegerField(label="Idade", validators=[DataRequired()])
    altura = FloatField(label="Altura", validators=[DataRequired()])
    peso = FloatField(label="Peso", validators=[DataRequired()])
    frequencia = IntegerField(label="Quantos minutos por semana em média você pratica exercícios físicos?")
    botao_submit_criarconta = SubmitField('Criar Conta')

    def validate_email(self, email):
        usuario = Usuario.query.filter_by(email=email.data).first()
        if usuario:
            raise ValidationError("Email já cadastrado. Cadastre-se com outro email ou faça login para continuar.")


class FormLogin(FlaskForm):
    email = StringField("E-mail", validators=[DataRequired(), Email()])
    senha = PasswordField("Senha", [DataRequired(), Length(6, 20)])
    lembrar_dados = BooleanField("Lembrar dados de acesso")
    botao_submit_login = SubmitField("Login")


class FormEditarPerfil(FlaskForm):
    username = StringField('Nome de Usuário', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    botao_submit_editarperfil = SubmitField('Confirmar edição')
    foto_perfil = FileField('Atualizar foto de perfil', validators=[FileAllowed(['jpg', 'png'])])
    idade = IntegerField(label="Idade", validators=[DataRequired()])
    altura = FloatField(label="Altura", validators=[DataRequired()])
    peso = FloatField(label="Peso", validators=[DataRequired()])
    frequencia = IntegerField(label="Quantos minutos por semana em média você pratica exercícios físicos?",
                              validators=[DataRequired()])

    def validate_email(self, email):
        if current_user.email != email.data:
            usuario = Usuario.query.filter_by(email=email.data).first()
            if usuario:
                raise ValidationError("Email já cadastrado. Insira outro email para continuar.")
