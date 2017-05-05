import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:

	@staticmethod
	def init_app(app):
		pass
		
	SECRET_KEY='You Shall Not Pass'	
	SQLALCHEMY_DATABASE_URI = 'sqlite:///'+os.path.join(basedir,'data.sqlite')
	SQLALCHEMY_COMMIT_ON_TEARDOWN = True
	SQLALCHEMY_TRACK_MODIFICATIONS = True
	UPLOADED_FILES_DEST = os.getcwd()
class DevelopmentConfig(Config):
	DEBUG = True

config={'default':DevelopmentConfig}