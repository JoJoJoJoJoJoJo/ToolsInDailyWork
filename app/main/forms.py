#-*-coding:utf-8-*-
from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import *
from .. import files
from flask_wtf.file import FileAllowed,FileField

class ProjectNameForm(FlaskForm):
	name = SelectField(u'选择项目')
	confirm = SubmitField(u'确定')
	
	def __init__(self,*args,**kwargs):
		super(ProjectNameForm,self).__init__(*args,**kwargs)
		self.name.choices = [('naruto',u'火影'),('dragonball',u'龙珠')]
		
class PathForm(FlaskForm):
	path = StringField(u'请输入目标文件夹路径',validators=[Required()])
	submit = SubmitField(u'提交')

class ItemForm(FlaskForm):
	name = StringField(u'道具名',validators=[Optional()])
	item_id = IntegerField(u'道具id',validators=[Optional(),NumberRange(10000000,20000000)])
	function_id = IntegerField(u'功能id',validators=[Optional(),NumberRange(0,12000000)])
	language = SelectField(u'语言版本',choices=[('ALL',u'全部'),('CN',u'国内'),('US','NA'),('FR',u'法语'),('BR',u'巴西'),('TH',u'泰语')])
	submit = SubmitField(u'查询')
	
class ImportForm(FlaskForm):
	csv = FileField(u'请提交csv文件',validators=[Required(),FileAllowed(files,u'只限csv文件！')])
	submit = SubmitField(u'提交')
	
class ItemEditForm(FlaskForm):
	name = StringField(u'道具名称',validators=[Required()])
	item_id = IntegerField(u'道具id',validators=[Required(),NumberRange(0,20000000)])
	function_id = IntegerField(u'功能id',validators=[NumberRange(0,12000000)])
	comment = StringField(u'备注',validators=[Optional()])
	language = SelectField(u'语言版本',choices=[('CN',u'国内'),('US','NA'),('FR',u'法语'),('BR',u'巴西'),('TH',u'泰语')])
	project = RadioField(u'项目',choices=[('naruto',u'火影'),('dragonball',u'龙珠')])
	submit = SubmitField(u'提交')
	
class ActivitySearchForm(FlaskForm):
	name = StringField(u'活动名称',validators=[Optional()])
	activity_id = IntegerField(u'活动id',validators=[Optional(),NumberRange(0,200)])
	submit = SubmitField(u'查询')
	
class ActivityEditForm(FlaskForm):
	name = StringField(u'活动名称',validators=[Required()])
	activity_id = IntegerField(u'道具id',validators=[Required(),NumberRange(0,200)])
	art_id = IntegerField(u'艺术字id',validators=[Optional(),NumberRange(0,100)])
	project = RadioField(u'项目',choices=[('naruto',u'火影'),('dragonball',u'龙珠')])
	submit = SubmitField(u'提交')
	
class ArtIdForm(FlaskForm):
	activity = StringField(u'活动列表',validators=[DataRequired()])
	#同一页面上的两个表单，判断是通过字典{'submit':True},所以要不同的名字
	submit1 = SubmitField(u'提交')
	
class ItemIdForm(FlaskForm):
	names = StringField(u'道具列表',validators=[Required()])
	#language = SelectField(u'语言版本',choices=[('ALL',u'全部'),('CN',u'国内'),('US','NA'),('FR',u'法语'),('BR',u'巴西'),('TH',u'泰语')])
	submit2 = SubmitField(u'提交')
	
class PackForm(FlaskForm):
	items = StringField(u'道具',validators=[Required()])
	language = SelectField(u'语言版本',choices=[('ALL',u'全部'),('CN',u'国内'),('US','NA'),('FR',u'法语'),('BR',u'巴西'),('TH',u'泰语')])
	submit3 = SubmitField(u'提交')
	
class ServerForm(FlaskForm):
	project = RadioField(u'项目',choices=[('naruto',u'火影'),('dragonball',u'龙珠')])
	platform = StringField(u'平台',validators=[Required()])
	server = IntegerField(u'服务器',validators=[Required(),NumberRange(0,2000)])
	date = DateField(u'开服日期',validators=[Required()])
	time = StringField(u'开服时间',validators=[Required(),Regexp(r'^(0[0-9]|1[0-9]|2[0-3]|[0-9])\:(0[0-9]|1[0-9]|2[0-9]|3[0-9]|4[0-9]|5[0-9]|[0-9])$')])
	submit = SubmitField(u'提交')