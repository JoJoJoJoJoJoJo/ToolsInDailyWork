#-*-coding:utf-8-*-

from . import db
from flask import current_app
from flask_login import UserMixin
from datetime import datetime,date,timedelta
import calendar


class Items(db.Model):
	__tablename__ = 'items'
	id = db.Column(db.Integer,primary_key=True)
	name = db.Column(db.String(64))
	item_id = db.Column(db.BigInteger,index=True)
	function_id = db.Column(db.BigInteger,default=0)
	language_version = db.Column(db.String(64),default='CN')
	project = db.Column(db.String(64))
	comment = db.Column(db.String(64))
	
	@property
	def chinese(self):
		if self.comment:
			return self.comment
		else:
			item = Items.query.filter_by(item_id=self.item_id,project=self.project,language_version='CN').first()
			if item:
				return item.name
			
	def __repr__(self):
		return u'<project:%r;name:%r>'%(self.project,self.name)
	

		
class Activity(db.Model):
	__tablename__ = 'activity'
	id = db.Column(db.Integer,primary_key=True)
	name = db.Column(db.String(64))
	activity_id = db.Column(db.Integer,index=True)
	art_id = db.Column(db.Integer)
	project = db.Column(db.String(64))
	
	def __repr__(self):
		return u'<project：%r;name：%r>'%(self.project,self.name)
		
		
class ServerInfo(db.Model):
	__tablename__ = 'new_server'
	id = db.Column(db.Integer,primary_key=True)
	server_id = db.Column(db.Integer,index=True)
	platform = db.Column(db.String(64))
	date = db.Column(db.Date)
	time = db.Column(db.String(32))
	project = db.Column(db.String(64))
	
	def __repr__(self):
		return u'<project: %r;platform: %r;server: %r;date: %r>'%(self.project,self.platform,self.server_id,self.date)
		
class User(db.Model,UserMixin):
	__tablename__ = 'users'
	id = db.Column(db.Integer,primary_key=True)
	name = db.Column(db.String(64))
	role_id = db.Column(db.Integer,db.ForeignKey('roles.id'))
	
	def __init__(self,**kwargs):
		super(User,self).__init__(**kwargs)
		if self.role is None:
			if self.name == current_app.config['AUTHOR']:
				self.role = Role.query.filter_by(name='Admin').first()
			if self.role is None:
				self.role = Role.query.filter_by(name='Users').first()
				
	def cal_leave_amount(self,hours,minutes):
		sum1 = sum(hours)
		sum2 = sum(minutes)
		while sum2>150:
			m = max(minutes)
			minutes.pop(minutes.index(m))
			sum1 += 1
			sum2 = sum(minutes)
		return 'hours:%s,minutes:%s'%(sum1,sum2)
			
	def cal_leave(self,month=date.isoformat(date.today())):
		'''
			param:
				month:%y-%m
		'''
		current_month = date.isoformat(date.today())
		if month is current_month:
			end_date = date.today-timedelta(days=1)
		else:
			end_date = date(int(month[:4]),int(month[5:7]),calendar.monthrange(int(month[:4]),int(month[5:7]))[-1])
		start_date = date(int(month[:4]),int(month[5:7]),1)
		schedules = Schedule.query.filter_by(user=self.name).filter(Schedule.date>start_date,Schedule.date<end_date).all()
		hours = []
		minutes = []
		for schedule in schedules:
			hours.append(schedule.late.get('hour'))
			minutes.append(schedule.late.get('minutes')) 
		result = self.cal_leave_amount(hours,minutes)
		return result
		
		
		
	def __repr__(self):
		return u'<User: %r; Role: %r>'%(self.name,self.role)
		
class Role(db.Model):
	__tablename__ = 'roles'
	id = db.Column(db.Integer,primary_key=True)
	name = db.Column(db.String(64),unique=True)
	users = db.relationship('User',backref='role',lazy='dynamic')

	@staticmethod
	def insert_roles():
		roles=['Admin','User','Visitor']
		for r in roles:
			role = Role.query.filter_by(name=r).first()
			if role is None:
				role = Role(name=r)
			db.session.add(role)
		db.session.commit()
		
	def __repr__(self):
		return '<Role %r>' %self.name
		
class Schedule(db.Model):
	__tablename__ = 'schedule'
	id = db.Column(db.Integer,primary_key=True)
	in_time = db.Column(db.DateTime,default=datetime.utcnow)
	out_time = db.Column(db.DateTime,default=datetime.utcnow)
	user = db.Column(db.String(64),db.ForeignKey('users.name'))
	date = db.Column(db.Date,default=date.today,unique=True)
	
	@property
	def late(self):
		yesterday = self.date-timedelta(days=1)
		#判断昨天是否为工作日
		is_yesterday_work = Schedule.query.filter_by(date=yesterday).first()
		#分界线为22:00
		standard_out_time = datetime.strptime(str(yesterday),'%Y-%m-%d') + timedelta(hours=22)
		if is_yesterday_work is None:
			stop_time = standard_out_time
		else:
			stop_time = is_yesterday_work.out_time
		if stop_time > standard_out_time:
			#下班时间晚于分界线
			standard_time = stop_time + timedelta(hours=12)
		else:
			standard_time = datetime.strptime(str(self.date),'%Y-%m-%d') + timedelta(hours=10)
		start_time = self.in_time
		if start_time > standard_time:
			return {'hour':(start_time-standard_time).seconds/3600,'minutes':(start_time-standard_time).seconds%3600/60}
		else:
			return {'hour':0,'minutes':0}
	
	def __repr__(self):
		return '<User:%r,date:%r,time:%r to %r,>'%(self.user,self.date,self.in_time,self.out_time)