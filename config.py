#-*-coding:utf-8-*-
import os
from celery.schedules import crontab

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
	MAIL_SERVER = 'smtp@163.com'
	MAIL_PORT = 25
	MAIL_USE_TLS = True
	MAIL_UESRNAME = os.environ.get('MAIL_USERNAME') or 'whr428@163.com'
	MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
	FLASKY_MAIL_SENDER = 'whr'
	FLASK_ADMIN = 'whr428@163.com'
	CELERY_BROKER_URL = 'redis://localhost'
	BROKER_URL = 'redis://localhost'
	CELERY_RESULT_BACKEND = 'redis://localhost'
	CELERY_TASK_SERIALIZER = 'json'
	CELERY_TASK_RESULT_EXIPRES = 1800
	
	CELERYBEAT_SCHEDULE = {
		'day-every-minute':{
			'task':'app.email.send_mail',
			#'schedule':crontab(hour=11,minute=05),
			'args':(FLASK_ADMIN,u'明日新服','mail/server')
			}
		}

class DevelopmentConfig(Config):
	DEBUG = True

config={'default':DevelopmentConfig,
	'base':Config}