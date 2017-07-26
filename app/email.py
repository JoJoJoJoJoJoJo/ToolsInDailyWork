from app import mail
from flask_mail import Message
from flask import current_app,render_template
from app import celery,create_app
import time,datetime,os

#app=create_app(os.getenv('FLASK_CONFIG') or 'default')
#app.app_context().push()

#@celery.task
def send_mail(to,subject,template,**kwargs):
	app = current_app._get_current_object()#why?
	#with app.app_context():
	#to avoid json issue about Message object
	msg = {'subject':subject,'sender':app.config['FLASKY_MAIL_SENDER'],'recipients':[to]}
	#msg = Message(subject,sender=app.config['FLASKY_MAIL_SENDER'],recipients=[to])
	body = render_template(template+'.txt',**kwargs)
	html = render_template(template+'.html',**kwargs)
	return send_async_email.delay(msg,body,html,**kwargs)

@celery.task(bind=True)
def send_async_email(self,msg,body,html,**kwargs):
	#need an app_context here
	app = create_app('default')
	app.app_context().push()
	#current_time = time.asctime()
	#tomorrow = datetime.date.today()+datetime.timedelta(1)
	#servers = ServerInfo.query.filter_by(date=tomorrow).all()
	message = Message(msg['subject'],sender=msg['sender'],recipients=msg['recipients'])
	message.body = body
	message.html = html
	mail.send(message)
	self.update_state(state='SUCCESS')
	return 'success!'