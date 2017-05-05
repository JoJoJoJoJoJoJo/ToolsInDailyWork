#-*-coding:utf-8-*-

from . import db

class Items(db.Model):
	__tablename__ = 'items'
	id = db.Column(db.Integer,primary_key=True)
	name = db.Column(db.String(64))
	item_id = db.Column(db.BigInteger,index=True)
	function_id = db.Column(db.BigInteger,default=0)
	language_version = db.Column(db.String(64),default='CN')
	project = db.Column(db.String(64))
	
	def __repr__(self):
		return u'<项目:%s;道具名称:%s>'%(self.project,self.name)
	

		
class Activity(db.Model):
	__tablename__ = 'activity'
	id = db.Column(db.Integer,primary_key=True)
	name = db.Column(db.String(64))
	activity_id = db.Column(db.Integer,index=True)
	art_id = db.Column(db.Integer)
	project = db.Column(db.String(64))
	
	def __repr__(self):
		return u'<项目：%s;活动名称：%s>'%(self.project,self.name)
		