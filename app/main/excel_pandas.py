#-*-coding:utf-8-*-

import os
import pandas as pd
from xlrd import XLRDError
import numpy as np
import sys


basedir = os.getcwd()

class ArgsError(StandardError):
	pass

class MakePivotByPandas(object):
	
	def __init__(self,path=None):
		self.path = path
		self.new_table = None
		self.datas = None
		self.tables = None
		
	def read_data(self):
		#读取excel中的数据，返回一个列表
		file_list = os.listdir(self.path)
		excels = [f for f in file_list if os.path.splitext(f)[1] == '.xlsx' or os.path.splitext(f)[1] == '.xls']
		if not excels:
			raise ArgsError(u'未发现excel文件！')
		datas = []
		for excel in excels:
			file=os.path.join(self.path,excel)
			try:
				data = pd.read_excel(file,index_col=0,na_values=['NA'])
			except XLRDError:
				data = pd.read_csv(file,sep='\t',encoding='gbk',index_col=0,na_values=['NA'])
				#这文件看起来是个excel，实际上它是个csv...
			except IOError:
				raise IOError
			datas.append(data)
		self.datas = datas

	def make_pivot_table(self):
		tables = []
		#对于列表中的每一列做一个数据透视表，返回所有数据透视表为一个列表
		for data in self.datas:
			table = pd.pivot_table(data,
				values=data.columns[2:],#[u'总安装',u'新安装',u'创号',u'创号率',u'最高在线',u'DAU',u'总次数',u'每日金币',u'每日金额',u'每日次数',u'每日人数','DARPPU','PAYRATE'].reverse(),
				index = data.index,
				aggfunc = np.sum)
			#确保数据透视表不为NA，也即原数据不为NA
			if table.values.any():
				tables.append(table)
		self.tables=tables

	def merge_table(self):
		#添加一个新的表格
		new_table = pd.DataFrame(0,
			index=self.tables[0].index,
			columns=self.tables[0].columns)
		for table in self.tables:
			#合并所有表格中具有相同index的数据
			#index不同的列结果会返回空
			try:
				new_table += table
			except TypeError:
				raise TypeError
		self.new_table=new_table
		x=0
		for i in [u'服务器',u'总安装数',u'新安装数',u'创号人数',u'创号率',u'最高在线',u'日活跃数',u'充值总次数',u'每日充值金币',u'每日充值金额',u'每日充值次数',u'每日充值人数','darppu','Pay rate']:
			try:
				data=self.new_table.pop(i)
				self.new_table.insert(x,i,data)
			except KeyError:
				self.new_table.insert(x,i,'null')
			x+=1
		
	def set_path(self):
		if not self.path:
			self.path = basedir
		
	def run(self,path=None):
		print u'''
		注意事项:
		1.必须先关闭所有excel并把所有excel放到同一文件夹中
		2.所有excel第一列保持相同，也即拥有相同的index（放在实际应用中就是开始与结束时间一致）
		3.最后输出的excel各列的排布会有混乱，需要手动调整
		-----------------------------------------------------------------------------------------------'''
		
		self.set_path()
		#读取数据
		try:
			self.read_data()
		except ArgsError:
			raise ArgsError(u'文件路径错误或文件未关闭')
		except IOError or WindowsError:
			raise ArgsError(u'文件路径错误或文件未关闭')
		self.make_pivot_table()
		try:
			self.merge_table()
		except TypeError:
			raise TypeError(u'文件无法合并')
		self.new_table.to_excel('gaishu.xlsx',sheet_name='sheet1',path_or_buf=self.path)
		print u'处理完成！'

app = MakePivotByPandas()		
if __name__ == '__main__':
	app.run(path=None)