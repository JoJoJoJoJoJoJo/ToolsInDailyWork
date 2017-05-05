#-*-coding:utf-8-*-
from . import main
from flask import render_template,request,flash,make_response,send_file,redirect,url_for
from .forms import *
from .excel_pandas import *
import os
from .orders import *
import pandas as pd
from ..models import *

@main.route('/',methods=['GET','POST'])
def index():
	form = ProjectNameForm()
	project='naruto'
	if form.is_submitted():
		project= form.name.data
	return render_template('index.html',form=form,project=project)
	
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
	items = None
	if item_form.validate_on_submit():
		if item_form.name.data:
			items = Items.query.filter(Items.name.ilike('%'+item_form.name.data+'%')).filter_by(project=project)
		elif item_form.item_id.data:
			items = Items.query.filter_by(item_id=item_form.item_id.data,project=project)
		elif item_form.function_id.data:
			items = Items.query.filter_by(function_id=item_form.function_id.data,project=project)
		else:
			items = Items.query.filter_by(project=project)
		if item_form.language.data == 'ALL':
			items = items.paginate(page,per_page=20,error_out=False)
		else:
			items = items.filter_by(language_version=item_form.language.data).paginate(page,per_page=20,error_out=False)
	#为了实现在没有查询时显示所有道具
	if not items:
		items = Items.query.filter_by(project=project).paginate(page,per_page=20,error_out=False)
	pagination = [{'item_id':item.item_id,
		'name':item.name,
		'function_id':item.function_id,
		'project':item.project,
		'language':item.language_version} for item in items.items]
		
	import_form = ImportForm()
	if import_form.validate_on_submit():
		filename = files.save(import_form.csv.data,name='items.csv')
		try:
			datas = pd.read_csv('items.csv',sep='\t',error_bad_lines=False,na_values=['NA'])
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
				new = Items.query.filter_by(item_id=id.astype(int),language_version=datas.loc[id,'language']).first()
				if new is None:
					new = Items(item_id=datas.loc[id,'item_id'].astype(int))
				new.function_id = datas.loc[id,'function_id'].astype(int)
				new.name = datas.loc[id,'name'].decode('utf-8')
				new.project = datas.loc[id,'project']
				new.language_version = datas.loc[id,'language']
				db.session.add(new)
			db.session.commit()
		os.remove(basedir+'\\items.csv')
			
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
		db.session.add(item)
		db.session.commit()
		return redirect(url_for('.items',project=project))
	form.item_id.data = item.item_id
	form.name.data = item.name
	form.function_id.data = item.function_id
	form.language.data = item.language_version
	form.project.data = item.project
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
		file.to_csv('app/download.csv',index_label=None,sep='\t')
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

@main.route('/others/')
def others():
	return 'nothing!'