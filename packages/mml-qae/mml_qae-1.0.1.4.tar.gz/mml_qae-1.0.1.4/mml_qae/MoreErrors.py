class MyError(Exception):
    pass

class DataError1(MyError):
	"""数据异常:给定的数组(或列表)不可被认为是可分析数据"""
	def __init__(self) -> None:
		pass
	def __str__(self) -> str:
		print("数据异常:给定的数组(或列表)不可被认为是可分析数据!")
		
class CSVError(MyError):
	"""读取异常:需要读取的{self.path}文件不存在或已损坏!"""
	def __init__(self,path) -> None:
		self.path=path
	def __str__(self) -> str:
		print(f"读取异常:需要读取的{self.path}文件不存在或已损坏!")     

class DataError2(MyError):
	"""数据异常:给定的数组(或列表)中含有意外的非数字项!"""
	def __init__(self) -> None:
		pass
	def __str__(self) -> str:
		print("数据异常:给定的数组(或列表)中含有意外的非数字项!")        
		
class DataError3(MyError):
	"""数据异常:指定的列名不存在"""
	def __init__(self) -> None:
		pass
	def __str__(self) -> str:
		print("数据异常:指定的列名不存在!")        
		
class DataError4(MyError):
	"""训练错误:给定的数组(或列表)在机器学习训练中出现异常"""
	def __init__(self) -> None:
		pass
	def __str__(self) -> str:
		print("训练错误:给定的数组(或列表)在机器学习训练中出现异常.请查看lists_of_number.py源码解决问题或在Git上联系作者: ZYpS_leader.")        
		
class DataError5(MyError):
	"""数据异常:需要分析的数据(或分析结果)包含inf或nan."""
	def __init__(self) -> None:
		pass
	def __str__(self) -> str:
		print("数据异常:需要分析的数据(或分析结果)包含inf或nan.")        