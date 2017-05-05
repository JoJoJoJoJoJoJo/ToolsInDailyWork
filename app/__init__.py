from flask import Flask
from flask_bootstrap import Bootstrap
from config import config
from flask_sqlalchemy import SQLAlchemy
from flask_uploads import UploadSet,configure_uploads

bootstrap = Bootstrap()
db = SQLAlchemy()
files = UploadSet('files',extensions=('csv'))

def create_app(config_name):
	app = Flask(__name__)
	app.config.from_object(config[config_name])
	config[config_name].init_app(app)
	
	bootstrap.init_app(app)
	db.init_app(app)
	configure_uploads(app,files)
	from .main import main as main_blueprint
	app.register_blueprint(main_blueprint)
	
	return app
	