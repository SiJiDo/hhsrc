from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
import os
import pymysql
import configparser

cfg = configparser.ConfigParser()
cfg.read('config.ini')

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'

DB_HOST = cfg.get("DATABASE", "DB_HOST")
DB_USER = cfg.get("DATABASE", "DB_USER")
DB_PASSWD = cfg.get("DATABASE", "DB_PASSWD")
DB_DATABASE = cfg.get("DATABASE", "DB_DATABASE")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://{}:{}@{}/{}".format(DB_USER, DB_PASSWD, DB_HOST, DB_DATABASE)
app.config["SECRET_KEY"] = '79537d00f4834892986f09a100aa1edf'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config["SQLALCHEMY_COMMIT_TEARDOWN"] = True

DB = SQLAlchemy(app)
login_manager.init_app(app)

from app.auth import auth as auth_blueprint
app.register_blueprint(auth_blueprint)

from app.main import main as main_blueprint
app.register_blueprint(main_blueprint)

from app.scanconfig import scanconfig as scanconfig_blueprint
app.register_blueprint(scanconfig_blueprint)

from app.scancorn import scancorn as scancorn_blueprint
app.register_blueprint(scancorn_blueprint)

from app.commonconfig import commonconfig as commonconfig_blueprint
app.register_blueprint(commonconfig_blueprint)

from app.targetManager import target as target_blueprint
app.register_blueprint(target_blueprint)

from app.subdomain import subdomain as subdomain_blueprint
app.register_blueprint(subdomain_blueprint)

from app.port import port as port_blueprint
app.register_blueprint(port_blueprint)

from app.url import url as url_blueprint
app.register_blueprint(url_blueprint)

from app.fileleak import fileleak as fileleak_blueprint
app.register_blueprint(fileleak_blueprint)

from app.vuln import vuln as vuln_blueprint
app.register_blueprint(vuln_blueprint)