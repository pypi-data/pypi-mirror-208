#对多组数字参数的分析: 通过多组数据判断某一特征的目标
import pandas as pd 
import numpy as np
from sklearn.model_selection import train_test_split as tts
from sklearn.neighbors import KNeighborsClassifier as knc 
from sklearn.metrics import accuracy_score as acc
import mml_qae.MoreErrors as me
def max_of_list(l:list):
    
    maxium=l[0]
    for i in l:
        try:
            i=float(i)
        except:
            raise me.DataError2   
    for j in range(0,len(l)-1):
        a=l[j];b=l[j+1]
        if b>a:
            maxium=b
    return maxium        

def cut(path:str,to_name:str,useless_name:str ):
    """给定csv文件路径path(以*.csv结尾)、csv文件中的目标组所在列名、csv文件中的无用列(如序号等)\n返回划分好的四个集合和初步预测模型"""
    try:data1=pd.read_csv(path,header=0)#读入csv数据
    except:raise me.CSVError
    try: 
        data=data1.drop([useless_name],axis=1)#去除无用的id列
        x_data=data.drop([to_name],axis=1)#从data中摘取特征组
        y_data=np.ravel(data[[to_name]])#从data中摘取目标组
    except:raise me.DataError3    
    x_trainset , x_testset , y_trainset , y_testset = tts(x_data,y_data,random_state=1)
    #建立训练集(训练特征组 和 训练目标组)和测试集(测试特征组 和 训练目标组)
    n=range(1,30)
    KNNs=[knc(n_neighbors=i) for i in n]
    scores=[KNNs[i].fit(x_trainset,y_trainset).score(x_testset,y_testset) for i in range(len(KNNs))]
    best=max_of_list(scores)
    model=knc(algorithm="kd_tree",n_neighbors=best)#建立基础模型,用kd_tree算法做超级参数
    return model,x_trainset,y_trainset,x_testset,y_testset

def check(path:str,to_name:str,useless_name:str ):
    """给定csv文件路径path(以*.csv结尾)、csv文件中的目标组所在列名、csv文件中的无用列(如序号等),返回模型预测准确度"""
    model,x_trainset,y_trainset,x_testset,y_testset=cut(path=path,to_name=to_name,useless_name=useless_name)
    model.fit(x_trainset,y_trainset) 
    y_predict=model.predict(x_testset) 
    score=acc(y_testset,y_predict)
    return score

def predict(path:str,to_name:str,useless_name:str,need_predict_list:list):
    """给定csv文件路径path(以*.csv结尾)、csv文件中的目标组所在列名、csv文件中的无用列(如序号等)、需要预测的数据列(以pandas阅读csv文件结果的list格式给入)\n返回预测后的数据目标,过程中如果有错误则返回127错误."""
    model,x_trainset,y_trainset,x_testset,y_testset=cut(path=path,to_name=to_name,useless_name=useless_name)
    model.fit(x_trainset,y_trainset) 
    try:
        y_predict=model.predict(need_predict_list) 
        return y_predict
    except:
        return me.DataError4
    
    #pip install -i https://pypi.org/project mml-qae