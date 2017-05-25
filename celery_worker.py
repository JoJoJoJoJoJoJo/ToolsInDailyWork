from app import create_app,celery
from app.email import send_mail

app = create_app('default')
app.app_context().push()

@celery.on_after_configure.connect
def setup_periodic_tasks(sender,**kwargs):
	sender.add_periodic_task(60.0,send_mail,name='-ass')
	