#!/usr/bin/env python
#-*-coding:utf-8-*-

from flask_script import Manager,Shell
import os
from app import create_app,db
from app.models import *
from flask_migrate import Migrate,MigrateCommand

app = create_app(os.environ.get('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app,db)

def make_shell_context():
	return dict(app=app,db=db,Server=ServerInfo,Activity=Activity,Items=Items)
	
manager.add_command('shell',Shell(make_context=make_shell_context))
manager.add_command('db',MigrateCommand)

@manager.command
def deploy():
	'''deploy'''
	from flask_migrate import upgrade
	from app.models import Items,Activity,ServerInfo
	
	upgrade()
	

if __name__ == '__main__':
	manager.run()