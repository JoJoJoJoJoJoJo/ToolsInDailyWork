#-*-coding:utf-8-*-
import os
from celery.schedules import crontab

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:

	@staticmethod
	def init_app(app):
		pass
		
	SECRET_KEY='You Shall Not Pass'	
	SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///'+os.path.join(basedir,'data.sqlite')
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

class ProductionConfig(Config):
	@classmethod
	def init_app(cls,app):
		Config.init_app(app)
		
		#LOGGING
		import logging
		from logging.handlers import SMTPHandler
		credentials = None
		secure = None
		if getattr(cls,'MAIL_USERNAME',None) is not None:
			credentials = (cls.MAIL_USERNAME,cls.MAIL_PASSWORD)
			if getattr(cls,'MAIL_USE_TLS',None):
				secure = ()
			mail_handler = SMTPHandler(
				mailhost=(cls.MAIL_SERVER,cls.MAIL_PORT),
				fromaddr=cls.FLASKY_MAIL_SENDER,
				toaddrs=[cls.FLASK_ADMIN],
				subject='Application Error',
				credentials=credentials,
				secure=secure)
			mail_handler.setLevel(logging.ERROR)
			app.logger.addHandler(mail_handler)
			

class DeployConfig(ProductionConfig):
	@classmethod
	def init_app(cls,app):
		ProductionConfig.init_app(app)
		
		#log in linux
		import logging
		from logging.handlers import SysLogHandler
		syslog_handler = SysLogHandler()
		syslog_handler.setLevel(logging.WARNING)
		app.logger.addHandler(syslog_handler)
		
config={'default':DevelopmentConfig,
	'base':Config,
	'production':ProductionConfig,
	'deploy':DeployConfig}