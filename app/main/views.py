#-*-coding:utf-8-*-
from . import main
from flask import render_template,request,flash,make_response,send_file,redirect,url_for,current_app,abort
from .forms import *
from .excel_pandas import *
import os
from .orders import *
import pandas as pd
from ..models import *
import json
import datetime
import time
from ..email import send_mail

@main.route('/',methods=['GET','POST'])
def index():
	form = ProjectNameForm()
	project='naruto'
	if form.is_submitted():
		project= form.name.data
	return render_template('index.html',form=form,project=project)
	
@main.route('/check-in/<name>')
def check_in(name):
	date = datetime.date.today()
	user = User.query.filter_by(name=name).first()
	if user is None:
		flash(u'未找到用户，请先注册')
	schedule = Schedule.query.filter_by(date=date,user=name).first()
	if schedule is None:
		schedule = Schedule(user=name,date=date)
	schedule.in_time = datetime.datetime.utcnow()
	db.session.add(schedule)
	db.session.commit()
	flash(u'上班时间记录成功')
	return redirect(url_for('.index'))
	
@main.route('/check-out/<name>')
def check_out(name):
	date = datetime.date.today()
	schedule = Schedule.query.filter_by(date=date,user=name).first()
	if schedule is None:
		flash(u'缺少上班记录，已填默认值，请稍后联系管理员修改')
		schedule = Schedule(user=name,date=date)
	schedule.out_time = datetime.datetime.utcnow()
	db.session.add(schedule)
	db.session.commit()
	flash(u'下班时间记录成功')
	return redirect(url_for('.index'))

@main.route('/outline/<project>',methods=['GET','POST'])
@main.route('/outline/',methods=['GET','POST'])
def outline(project='naruto'):
	form = PathForm()
	if form.validate_on_submit():
		path = form.path.data
		pivot = MakePivotByPandas(path)
		try:
			pivot.read_data()
		except IOError:
			flash(u'路径错误或文件未关闭，请确认后重试！')
		else:
			pivot.make_pivot_table()
			try:
				pivot.merge_table()
			except TypeError:
				flash(u'表格无法合并，请检查数据')
			else:
				new_file = os.path.join(path,'new.xlsx')
				pivot.new_table.to_excel(new_file,sheet_name='sheet1')
				flash(u'处理完成！')
		
	return render_template('outline.html',form=form,project=project)
		
@main.route('/orders/<project>',methods=['GET','POST'])
def orders(project):
	form = PathForm()
	orders = Revenue()
	if form.validate_on_submit():
		path = form.path.data
		orders = Revenue(path)
		try:
			orders.read_data()
		except IOError:
			flash(u'路径错误或文件未关闭，请确认后重试')
		else:
			orders.merge_tables()
			orders.sort_and_sum()
	dates = orders.amount.keys()
	dates.sort()
	dates.reverse()
	return render_template('orders.html',form=form,project=project,revenue=orders.amount,dates=dates)
	
@main.route('/items/<project>',methods=['GET','POST'])
def items(project):
	item_form = ItemForm()
	page = request.args.get('page',1,type=int)
	items = Items.query.filter_by(project=project).paginate(page,per_page=20,error_out=False)
	name = request.args.get('name')
	if name and not item_form.validate_on_submit():
		item_form.name.data = name
		items = Items.query.filter(Items.name.ilike('%'+item_form.name.data+'%')).filter_by(project=project).paginate(page,per_page=20,error_out=False)
	if item_form.validate_on_submit():
		if item_form.name.data:
			items = Items.query.filter(Items.name.ilike('%'+item_form.name.data+'%')).filter_by(project=project)
			current_app.logger.log(20,'searching %s'%item_form.name.data)
		elif item_form.item_id.data:
			items = Items.query.filter_by(item_id=item_form.item_id.data,project=project)
		elif item_form.function_id.data:
			items = Items.query.filter_by(function_id=item_form.function_id.data,project=project)
		else:
			items = Items.query.filter_by(project=project)
		if item_form.language.data == 'ALL':
			#新的查询重置页码
			items = items.paginate(1,per_page=20,error_out=False)
		else:
			items = items.filter_by(language_version=item_form.language.data).paginate(1,per_page=20,error_out=False)
		
	#为了实现在没有查询时显示所有道具
	#if not items:
		#items = Items.query.filter_by(project=project).paginate(page,per_page=20,error_out=False)
	pagination = [{'item_id':item.item_id,
		'name':item.name,
		'function_id':item.function_id,
		'project':item.project,
		'language':item.language_version,
		'comment':item.comment,
		'chinese':item.chinese} for item in items.items]
		
	import_form = ImportForm()
	if import_form.validate_on_submit():
		#filename = files.save(import_form.csv.data,name='items.csv')
		try:
			datas = pd.read_csv(import_form.csv.data,sep='\t',error_bad_lines=False,na_values=['NA'])
		except XLRDError:
			flash(u'csv文件无法读取！')
		#判定csv中是否有这几个列
		#写的很奇怪，不备注我自己都看不懂
		#对datas.columns中的每一项判断是否在列表中，然后set去重，如果全是True就通过
		#pandas应该有这方面的支持？
		if not set(map(lambda x:x in ['item_id','function_id','name','project','language'],datas.columns)) == set([True]):
			flash(u'csv文件格式错误！')
		else:
			for id in datas.index:
				#pandas读取到的数字需先转化成int型
				#字符串需要转化成string
				new = Items.query.filter_by(item_id=datas.loc[id,'item_id'].astype(int),language_version=datas.loc[id,'language']).first()
				if new is None:
					new = Items(item_id=datas.loc[id,'item_id'].astype(int))
				try:
					new.function_id = datas.loc[id,'function_id'].astype(int)
					new.name = datas.loc[id,'name'].decode('utf-8')
					new.project = datas.loc[id,'project']
					new.language_version = datas.loc[id,'language']
				except:
					print new.function_id
				db.session.add(new)
			db.session.commit()
		#os.remove(basedir+'\\items.csv')
			
	import_csv = bool(request.cookies.get('import'))
	return render_template('items.html',pagination=pagination,end_point='.items',form1=item_form,form2=import_form,project=project,csv=import_csv,items=items)

@main.route('/edit/<int:id>',methods=['POST','GET'])
def edit(id):
	language = request.args.get('language')
	project = request.args.get('project')
	item = Items.query.filter_by(item_id=id,language_version=language,project=project).first()
	form = ItemEditForm()
	if form.validate_on_submit():
		item.item_id = form.item_id.data
		item.name = form.name.data
		item.function_id = form.function_id.data
		item.language_version = form.language.data
		item.project = form.project.data
		item.comment = form.comment.data
		db.session.add(item)
		db.session.commit()
		return redirect(url_for('.items',project=project))
	form.item_id.data = item.item_id
	form.name.data = item.name
	form.function_id.data = item.function_id
	form.language.data = item.language_version
	form.project.data = item.project
	form.comment.data = item.comment
	return render_template('edit.html',project=project,form=form)

@main.route('/additem/<project>',methods=['GET','POST'])
def additem(project):
	form = ItemEditForm()
	if form.validate_on_submit():
		item = Items(
			item_id = form.item_id.data,
			name = form.name.data,
			function_id = form.function_id.data,
			project = form.project.data,
			language_version = form.language.data)
		db.session.add(item)
		db.session.commit()
		return redirect(url_for('.items', project=project))
	return render_template('edit.html',form=form)
	
@main.route('/delete_item/<id>')
def delete_item(id):
	project = request.args.get('project')
	resp = make_response(redirect(url_for('main.items',project=project)))
	language = request.args.get('language')
	item = Items.query.filter_by(item_id=id,project=project,language_version=language).first()
	db.session.delete(item)
	return resp
	
#这两个页面的代码重合度很高，应该可以写到一起传个参数作为判断依据的
@main.route('/atype/<project>',methods=['GET','POST'])
def atype(project):
	form_a = ActivitySearchForm()
	page = request.args.get('page',1,type=int)
	activities = None
	if form_a.validate_on_submit():
		if form_a.name.data:
			activities = Activity.query.filter(Activity.name.ilike('%'+form_a.name.data+'%')).filter_by(project=project)
		elif form_a.activity_id.data:
			activities = Activity.query.filter_by(activity_id=form_a.activity_id.data,project=project)
		else:
			activities = Activity.query.filter_by(project=project)
		activities = activities.paginate(page,per_page=20,error_out=False)
	#为了实现在没有查询时显示所有道具
	if not activities:
		activities = Activity.query.paginate(page,per_page=20,error_out=False)
	pagination = [{'activity_id':item.activity_id,
		'name':item.name,
		'art_id':item.art_id,
		'project':item.project,
		} for item in activities.items]
		
	import_form = ImportForm()
	if import_form.validate_on_submit():
		#这里其实没必要存，可以直接读
		filename = files.save(import_form.csv.data,name='activities.csv')
		try:
			datas = pd.read_csv('activities.csv',sep='\t',index_col=0,error_bad_lines=False,na_values=None)
		except XLRDError:
			flash(u'csv文件无法读取！')
		if not set(map(lambda x:x in ['activity_id','name','project','art_id'],datas.columns)) == set([True]):
			flash(u'csv文件格式错误！')
		else:
			for id in datas.index:
				new = Activity.query.filter_by(activity_id=id.astype(int)).first()
				if new is None:
					new = Activity(activity_id=id.astype(int))
				new.art_id = datas.loc[id,'art_id'].astype(int)
				new.name = datas.loc[id,'name'].decode('utf-8')
				new.project = datas.loc[id,'project']
				db.session.add(new)
			db.session.commit()
		os.remove(basedir+'\\activities.csv')
		return redirect(url_for('.cancel_import',end_point=end_point))
			
	import_csv = bool(request.cookies.get('import'))
	return render_template('activity.html',pagination=pagination,end_point='.atype',form1=form_a,form2=import_form,project=project,csv=import_csv,activities=activities)

@main.route('/edit_activity/<int:id>',methods=['POST','GET'])
def edit_activity(id):
	project = request.args.get('project')
	activity = Activity.query.filter_by(activity_id=id,project=project).first()
	form = ActivityEditForm()
	if form.validate_on_submit():
		activity.activity_id = form.activity_id.data
		activity.name = form.name.data
		activity.art_id = form.art_id.data
		activity.project = form.project.data
		db.session.add(activity)
		db.session.commit()
		return redirect(url_for('.atype',project=project))
	form.activity_id.data = activity.activity_id
	form.name.data = activity.name
	form.art_id.data = activity.art_id
	form.project.data = activity.project
	return render_template('edit_activity.html',project=project,form=form)

@main.route('/add_activity/<project>',methods=['GET','POST'])
def add_activity(project):
	form = ActivityEditForm()
	if form.validate_on_submit():
		activity = Activity(
			activity_id = form.activity_id.data,
			name = form.name.data,
			art_id = form.art_id.data,
			project = form.project.data,
			)
		db.session.add(activity)
		db.session.commit()
		return redirect(url_for('.atpye', project=project))
	return render_template('edit_activity.html',form=form)
	
@main.route('/delete_activity/<int:id>')
def delete_activity(id):
	project = request.args.get('project')
	resp = make_response(redirect(url_for('main.atype',project=project)))
	activity = Activity.query.filter_by(activity_id=id,project=project).first()
	db.session.delete(activity)
	return resp

@main.route('/export_csv/<end_point>')
def export(end_point):
	try:
		path=basedir+'\\app\\download.csv'
		os.remove(path)
	except WindowsError:
		pass
	if end_point == '.items':
		items = Items.query.all()
		file = pd.DataFrame(columns=['item_id','function_id','name','project','language'])
		for item in items:
			#建立一个以columns为index的dataframe然后转置
			#pd.Seires创建的是一个列而不是一行，所以不能直接append
			#pd的append与list的append不同，它不会改变原始对象的值
			file = file.append(pd.DataFrame([item.item_id,item.function_id,item.name,item.project,item.language_version],index=file.columns).T)
		file.to_csv('app/download.csv',index_label=None,sep='\t',encoding='utf-8')
	elif end_point == '.atype':
		activity = Activity.query.all()
		file = pd.DataFrame(columns=['activity_id','name','art_id','project'])
		for item in activity:
			file = file.append(pd.DataFrame([item.activity_id,item.name,item.art_id,item.project],index=file.columns).T)
		file.to_csv('app/download.csv',encoding='gbk',index_label=None,sep='\t')
	response = make_response(send_file('download.csv'))
	response.headers['Content-Disposition'] = 'attachment;filename=download.csv;'
	return response

@main.route('/import_csv/<end_point>')
def import_csv(end_point,project='naruto'):
	resp = make_response(redirect(url_for(end_point,project=project)))
	resp.set_cookie('import','1',max_age=60)
	return resp
	
@main.route('/cancel_import/<end_point>')
def cancel_import(end_point,project='naruto'):
	resp = make_response(redirect(url_for(end_point,project=project)))
	resp.set_cookie('import','',max_age=60)
	return resp

@main.route('/others/<project>',methods=['GET','POST'])
def others(project):
	art_form = ArtIdForm()
	ids = [6,8,9]
	#这样可以避免同一页面上的不同表单同时验证
	#先后顺序不能反
	if art_form.submit1.data and art_form.validate_on_submit():
		#这.. \n不生效，必须是' '
		#这样只能支持中文输入了... 英文之间的空格无法判定
		names = art_form.activity.data.split(' ')
		for name in names:
			activity = Activity.query.filter_by(name=name,project=project).first()
			if activity:
				ids.append(activity.art_id)
		#去除没有匹配到id的部分，也即去除None
		while True:
			try:
				ids.remove(None)
			except ValueError:#ValueError: list.remove(x): x not in list
				break
	
	item_form = ItemIdForm()
	items = {}
	list_of_items = []
	if item_form.submit2.data and item_form.validate_on_submit():
		names = item_form.names.data.replace('%n','').split(' ')
		for name in names:
			items={}#循环开始前需初始化
			item = Items.query.filter_by(name=name,project=project,language_version='CN').first()
			if item:
				items['id'] = item.id
				items['item_id'] = item.item_id
				items['name'] = item.name
				items['function_id'] = item.function_id
			items['input'] = name
			list_of_items.append(items)
		
	pack_form = PackForm()
	desc = ''
	item_json = None
	if pack_form.submit3.data and pack_form.validate_on_submit():
		items = pack_form.items.data.split('%n')#[item*n]
		for i in items:
			name,amount = i.split('*')
			item_from_comment = Items.query.filter_by(comment=name,project=project,language_version=pack_form.language.data).first()
			item_cn = Items.query.filter_by(name=name,project=project,language_version='CN').first()
			if item_cn:
				item_from_chinese = Items.query.filter_by(item_id=item_cn.item_id,project=project,language_version=pack_form.language.data).first()
			else:
				item_from_chinese = None
				#不优雅 这么多if
			if item_from_comment:
				item_desc = item_from_comment.name+'*'+amount+'%n'
				item_dict = dict([('amount',int(amount)),('code',item_from_comment.item_id),('type',1)])
				list_of_items.append(item_dict)
			elif item_from_chinese:
				item_desc = item_from_chinese.name+'*'+amount+'%n'
				item_dict = dict([('amount',int(amount)),('code',item_from_chinese.item_id),('type',1)])
				list_of_items.append(item_dict)
			else:
				item_desc = i+'CHINESE NOT FOUND  '
			desc += item_desc
			#去最后一个%n
		desc = desc[:-2]
		item_json = json.dumps(list_of_items)
	
	path_form = PathForm()
	if path_form.submit.data and path_form.validate_on_submit():
		with open (path_form.path.data,'a+') as f:
			lines = f.readlines()
			for line in lines:
				price1,price2,price3,price4,price5=line.split()
				price_list = map(dict,[
					[('rate','55000'),('price',price1)],
					[('rate','25000'),('price',price2)],
					[('rate','10000'),('price',price3)],
					[('rate','6000'),('price',price4)],
					[('rate','4000'),('price',price5)]])
				price_json = json.dumps(price_list)
				f.write('\n'+price_json)
			f.close()
		flash('successful')
	return render_template('others.html',form1=art_form,ids=ids,project=project,form2=item_form,form3=pack_form,form4=path_form,item_list=list_of_items,desc=desc,json=item_json)
	
@main.route('/new_servers/',methods=['GET','POST'])
def new_servers():
	project = request.args.get('project') or 'naruto'
	current_date = datetime.date.today()
	page = request.args.get('page',1,type=int)
	pagination = ServerInfo.query.filter(ServerInfo.date>=current_date).order_by(ServerInfo.date).paginate(page,per_page=20,error_out=False)
	servers = [{'id':item.id,
		'project':item.project,
		'platform':item.platform,
		'server_id':item.server_id,
		'date':item.date,
		'time':item.time} for item in pagination.items]
		
	form = ImportForm()
	if form.validate_on_submit():
		try:
			datas = pd.read_csv(form.csv.data,sep='\t',index_col=0)
		except XLRDError:
			flash(u'csv文件无法读取！')
		if not set(map(lambda x:x in ['id','project','platform','server','date','time'],datas.columns)) == set([True]):
			flash(u'csv文件格式错误！')
		else:
			for id in datas.index:
				new = ServerInfo(project=datas.loc[id,'project'].decode('utf-8'),
					platform=datas.loc[id,'platform'].decode('utf-8'),
					server_id=datas.loc[id,'server'].astype(int),
					date=datetime.datetime.strptime(datas.loc[id,'date'],'%Y-%m-%d'),
					time=datas.loc[id,'time'])
				db.session.add(new)
			db.session.commit()
		return redirect(url_for('.new_servers'))
	csv=bool(request.cookies.get('import'))
	return render_template('servers.html',project=project,pagination=pagination,servers=servers,csv=csv,form=form,end_point='.new_servers')
	
@main.route('/add_servers/',methods=['GET','POST'])
def add_servers():
	form = ServerForm()
	project = request.args.get('project') or 'naruto'
	if form.validate_on_submit():
		server = ServerInfo(project=form.project.data,
			platform = form.platform.data,
			server_id = form.server.data,
			date = form.date.data,
			time = form.time.data)
		db.session.add(server)
		db.session.commit()
		return redirect(url_for('main.new_servers',project=project))
	return render_template('edit.html',form=form,project=project)
	
@main.route('/edit_servers/<int:id>',methods=['GET','POST'])
def edit_servers(id):
	form = ServerForm()
	project = request.args.get('project') or 'naruto'
	server = ServerInfo.query.get_or_404(id)
	if form.validate_on_submit():
		server.project = form.project.data
		server.platform = form.platform.data
		server.server_id = form.server.data
		server.date = form.date.data
		server.time = form.time.data
		db.session.add(server)
		db.session.commit()
		return redirect(url_for('.new_servers',project=project))
	form.project.data = server.project
	form.platform.data = server.platform
	form.server.data = server.server_id
	form.date.data = server.date
	form.time.data = server.time
	return render_template('edit.html',form=form,project=project)
	
@main.route('/delete_servers/<int:id>')
def delete_servers(id):
	project = request.args.get('project') or 'naruto'
	resp = make_response(redirect(url_for('main.new_servers',proejct=project)))
	server = ServerInfo.query.get_or_404(id)
	db.session.delete(server)
	return resp
	
@main.route('/manage/<name>',methods=['GET','POST'])
def manage(name):
	u=User.query.filter_by(name=name).first()
	page = request.args.get('page',1,type=int)
	if not u:
		flash(u'用户不存在！')
		return redirect(url_for('.index'))
	admin = Role.query.filter_by(name='Admin').first()
	if u.role is not admin:
		abort(404)
	schedule = Schedule.query.filter_by(user=name).order_by(Schedule.date)
	if schedule is None:
		flash(u'尚未有任何记录')
	pagination = schedule.paginate(page,per_page=20,error_out=False)
	records = [{'in_time':item.in_time,
		'out_time':item.out_time,
		'date':item.date,
		'late':item.late} for item in pagination.items]
	return render_template('manage.html',name=name,pagination=pagination,records=records,total=u.cal_leave())
	
@main.route('/send_email/')
def send_email():
	print current_app.config['MAIL_USERNAME']
	print current_app.config['MAIL_PASSWORD']
	send_mail(current_app.config['FLASK_ADMIN'],'servers','mail/server')
	
	return 'success'
	
@main.route('/testing/',methods=['GET','POST'])
def testing():
	#if request.get_json('l'):
	#	return '<h1>ahahahahahahaha</h1>'	
	return 'success'

@main.route('/test',methods=['GET','POST'])
def test():
	return render_template('test.html')

@main.after_request
def removeHeader(resp):
	resp.headers['Server']=''
	return resp
	
@main.context_processor
def inject_checked():
	date = datetime.date.today()
	today = Schedule.query.filter_by(date=date).first()
	checked = False
	if today:
		checked = today.in_time
	name = 'whr'
	return dict(checked=checked,name=name)