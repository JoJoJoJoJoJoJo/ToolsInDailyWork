from app import mail
from flask_mail import Message
from flask import current_app,render_template
from app import celery
from app.models import ServerInfo
import time,datetime

#@celery.task
def send_mail(to,subject,template,**kwargs):
	app = current_app._get_current_object()#why?
	#to avoid json issue about Message object
	msg = {'subject':subject,'sender':app.config['FLASKY_MAIL_SENDER'],'recipients':[to]}
	#msg = Message(subject,sender=app.config['FLASKY_MAIL_SENDER'],recipients=[to])
	#msg.body = render_template(template+'.txt',servers=servers)
	#msg.html = render_template(template+'.html',servers=servers)
	send_async_email(msg,template,**kwargs)

#@celery.task(name='app.email.send_async_email')
def send_async_email(msg,template,**kwargs):
	#with app.app_context():
	current_time = time.asctime()
	tomorrow = datetime.date.today()+datetime.timedelta(1)
	servers = ServerInfo.query.filter_by(date=tomorrow).all()
	message = Message(msg['subject'],sender=msg['sender'],recipients=msg['recipients'])
	message.body = render_template(template+'.txt',servers=servers)
	message.html = render_template(template+'.html',servers=servers)
	mail.send(message)
