from flask import Flask
from flask_bootstrap import Bootstrap
from config import config
from flask_sqlalchemy import SQLAlchemy
from flask_uploads import UploadSet,configure_uploads
from flask_mail import Mail
from celery import Celery


bootstrap = Bootstrap()
db = SQLAlchemy()
files = UploadSet('files',extensions=('csv'))
mail = Mail()
celery = Celery(__name__,broker=config['base'].CELERY_BROKER_URL,backend=config['base'].CELERY_RESULT_BACKEND)

def create_app(config_name):
	app = Flask(__name__)
	app.config.from_object(config[config_name])
	config[config_name].init_app(app)
	bootstrap.init_app(app)
	db.init_app(app)
	configure_uploads(app,files)
	mail.init_app(app)
	celery.conf.update(app.config)
	
	from .main import main as main_blueprint
	app.register_blueprint(main_blueprint)
	
	return app
	