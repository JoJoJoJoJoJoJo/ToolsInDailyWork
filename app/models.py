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
		return u'<project:%s;name:%s>'%(self.project,self.name)
	

		
class Activity(db.Model):
	__tablename__ = 'activity'
	id = db.Column(db.Integer,primary_key=True)
	name = db.Column(db.String(64))
	activity_id = db.Column(db.Integer,index=True)
	art_id = db.Column(db.Integer)
	project = db.Column(db.String(64))
	
	def __repr__(self):
		return u'<project：%s;name：%s>'%(self.project,self.name)
		
		
class ServerInfo(db.Model):
	__tablename__ = 'new_server'
	id = db.Column(db.Integer,primary_key=True)
	server_id = db.Column(db.Integer,index=True)
	platform = db.Column(db.String(64))
	date = db.Column(db.Date)
	time = db.Column(db.String(32))
	project = db.Column(db.String(64))
	
	def __repr__(self):
		return u'<project: %s;platform: %s;server: %s;date: %s>'%(self.project,self.platform,self.server_id,self.date)