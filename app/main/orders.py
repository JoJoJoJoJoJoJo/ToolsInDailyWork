#-*-coding:utf-8-*-
import pandas as pd
import os
from xlrd import XLRDError

basedir = os.getcwd()

class ArgsError(StandardError):
	pass

	
class Revenue():
	def __init__(self,path=None):
		self.path = path
		self.datas = []
		self.table = None
		self.amount={}
		
	def set_path(self):
		if not self.path:
			self.path = basedir
	
	def read_data(self):
		#不做交互的话暂时可不考虑错误及异常
		file_list = os.listdir(self.path)
		excels = [f for f in file_list if os.path.splitext(f)[1] == '.xlsx' or os.path.splitext(f)[1] == '.xls']
		
		if not excels:
			raise ArgsError(u'目标路径下没有excel文件')
			
		for excel in excels:
			#取绝对路径以方便调用
			file = os.path.join(self.path,excel)
			try:
				data = pd.read_excel(file,index_col=0,encoding='gbk',na_values=['NA'])
			except XLRDError:
				data = pd.read_csv(file,sep='\t',encoding='gbk',index_col=0,na_values=['NA'])
				
			self.datas.append(data)
		
	def merge_tables(self):
		ori_table = pd.DataFrame(columns=self.datas[0].columns)
		for table in self.datas:
			ori_table = ori_table.append(table)
		self.table = ori_table
		
	def sort_and_sum(self):
		'''所有第三方订单金额归零
		noneed = self.table[self.table[u'订单号'].str.startswith('yeyoye')]
		noneed.loc[:,u'支付总额'] = 0'''
		#日期去除时间
		i = 0
		for time in self.table[u'订单日期']:
			self.table.iloc[i,5] = time[:10]#第五列是日期
			i+=1
			#self.table[u'订单日期'][time] = pd.Period(time,'D')
		#按照日期筛选后求和
		dates = set(self.table[u'订单日期'])
		for date in dates:
			#求出第三方订单金额并扣除
			noneed = self.table[(self.table[u'订单号'].str.startswith('\'yeyoye'))&(self.table[u'订单日期']==date)][u'支付总额'].sum()
			self.amount.setdefault(date)
			self.amount[date]=(self.table[self.table[u'订单日期']==date][u'支付总额'].sum() - noneed)/10
				
	def output(self):
		l = self.amount.keys()
		l.sort()
		l.reverse()
		for key in l:
			print u'日期:%s 金额：%s'%(key,self.amount[key])
			
if __name__ == '__main__':
	app = Revenue(path=None)
	app.set_path()
	app.read_data()
	app.merge_tables()
	app.sort_and_sum()
	app.output()