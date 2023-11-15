from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
import os

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)

app.config['SECRET_KEY'] = '44495c599ff7e41b640de11a238f0898'
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'alert-info'

from comunidade import routes

