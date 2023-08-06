import matplotlib.pyplot as plt 
import statsmodels.api as sm
import numpy as np 
import mml_qae.MoreErrors as me
def make_results(lista,listb,i=False):#给定两列表返回预测组 
    """给定两个列表(顺序:特征组,目标组)\n i值默认为假,不打印模型准确度;为真则打印准确度""" 
    X=lista
    Y=listb
    dX=np.column_stack((X,np.power(X,2),np.power(X,3),np.power(X,4),np.sin(X),np.tan(X),np.cos(X)  ))
    X_added=sm.add_constant(dX)
    model=sm.OLS(Y,X_added)
    results=model.fit() 
    if i:
        print("本次精度为",results.rsquared*100,"%") 
    return results
def draw(X,Y):
    """给定两个列表(顺序:特征组,目标组)\n无返回值,但直接打开模型预测的可视化界面""" 
    results=make_results(X,Y)
    Y_predict=results.predict()
    plt.scatter(X,Y,color="blue",label="real")
    plt.plot(X,Y_predict,color="orange",label="predicted")
    plt.legend(loc='upper left')
    plt.show()
def predict(X:list,Y:list,x:float ):
    """给定两个列表(顺序:特征组,目标组)和需要预测的数字\n返回需要预测的数字的预测结果(如果返回0则说明该值存在问题(如inf或nan)"""
    results=make_results(X,Y)
    try:
        p=results.predict([1,x,np.power(x,2),np.power(x,3),np.power(x,4),np.sin(x),np.tan(x),np.cos(x)])
        return p
    except:
        raise me.DataError5