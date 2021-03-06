# flask-sovellus
from flask import Flask
app = Flask(__name__)

# tietokanta
from flask_sqlalchemy import SQLAlchemy

import os

if os.environ.get("HEROKU"):
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///messages.db"
    app.config["SQLALCHEMY_ECHO"] = True

db = SQLAlchemy(app)


# kirjautuminen
from os import urandom
app.config["SECRET_KEY"] = urandom(32)

from flask_login import LoginManager, current_user
login_manager = LoginManager()
login_manager.setup_app(app)

login_manager.login_view = "auth_login"
login_manager.login_message = "Please login to use this functionality."

# oman sovelluksen toiminnallisuudet
from application import views

from application.topics import models
from application.topics import views

from application.messages import models
from application.messages import views

from application.auth import models
from application.auth import views

from application.users import views
from application.search import views

# kirjautuminen, osa 2
from application.auth.models import User


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

# luodaan taulut tietokantaan tarvittaessa
try:
    db.create_all()
except:
    pass
