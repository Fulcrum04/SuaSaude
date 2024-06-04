from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
import os

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)

app.config['SECRET_KEY'] = 'b2deb66af296d0f6038efe5f0e3544ef'
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://suasaude_db_2smk_user:JDh976pnQlAODeE6SrzCIH0VHYMyWFAu@dpg-cpf54qrtg9os73b7o2bg-a.oregon-postgres.render.com/suasaude_db_2smk" #os.getenv('DATABASE_URL')

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'alert-info'

from SuaSaude import routes

