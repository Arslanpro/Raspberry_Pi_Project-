import os
import hashlib
from wake_up_bright.alarm_clock.app.crud.models import db
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from wake_up_bright.alarm_clock.app.crud.views import crud
basedir = os.path.abspath(os.path.dirname(__file__))


def create_app():
    app = Flask(__name__)
    # app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:123@127.0.0.1:3306/project"
    app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:1234567890@127.0.0.1:3306/project"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ECHO"] = False
    app.config["SECRET_KEY"] = 'secret'
    db.app = app
    db.init_app(app)
    app.register_blueprint(crud, url_prefix='/crud')
    return app
