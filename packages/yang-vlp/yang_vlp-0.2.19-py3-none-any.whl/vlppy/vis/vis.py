import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def draw_position_contrast(pred,true,title="",savepath=...,showfig=True):
    """预测位置和真实位置对比图
    Params
        pred: 预测位置
        true: 真实位置
        title: 标题
        savepath: 保存路径
        showfig: 是否显示图例
    """
    assert len(pred) == len(true) 
    pred = np.asarray(pred)
    # (n,2) or (n,3) -> (2,n) or (3,n)
    if pred.shape[-1] in (2,3):
        pred = np.transpose(pred)
        true = np.transpose(true)
    if pred.shape[0] == 2:
        plt.scatter(*pred, c='none',facecolors='none',edgecolors='r',linewidths=1)
        plt.scatter(*true, c='k',marker='+',linewidths=1)
    elif pred.shape[0] == 3:
        ax = plt.axes(projection='3d')
        ax.scatter3D(*pred, c='none',facecolors='none',edgecolors='r',linewidths=1)
        ax.scatter3D(*true, c='k',marker='+',linewidths=1)
    else: 
        plt.scatter(pred, c='none',linewidths=1, facecolors='none',edgecolors='r')
        plt.scatter(true, c='k', marker='+',linewidths=1)
    plt.title(title)
    plt.legend(['Predicted position','Actual position'])
    if savepath != ...:
        plt.savefig(savepath)
    if showfig:
        plt.show()

def draw_history(history,title="history",savepath=...,showfig=True):
    """绘制网络模型训练过程参数变换图
    Params
        history: 历史值
        title: 标题
        savepath: 保存路径
        showfig: 是否显示图例
    """
    data = pd.DataFrame(history)
    data.plot(figsize=(8,5))
    plt.grid(True)
    plt.title(title)
    plt.xlabel("Iter")
    if savepath != ...:
        plt.savefig(savepath)
    if showfig:
        plt.show()

def draw_error_hist(error,bins=10,rwidth=0.6,title="",savepath=...,showfig=True):
    """绘制误差分布直方图
    """
    # 解决中文乱码
    plt.rcParams["font.sans-serif"]=["SimHei"] #设置字体
    plt.rcParams["axes.unicode_minus"]=False #该语句解决图像中的“-”负号的乱码问题
    fre_tuple = plt.hist(error, bins=bins, rwidth=rwidth, align='left')
    # 绘制统计文本
    [plt.text(y, x, f'{int(x)}', ha='center', va= 'bottom', fontsize=10) for x,y in zip(*fre_tuple[:2])]
    plt.title(title)
    plt.xlabel("Position error")
    plt.ylabel("The number of position error")

    if savepath != ...:
        plt.savefig(savepath)
    if showfig:
        plt.show()
    return fre_tuple

def cdfplot(error,title="",savepath=...,showfig=True):
    """绘制经验误差积累分布图CDF
    Params 
        error: 误差数组
        title: 标题
        savepath: 保存路径
        showfig: 是否显示图例
    """
    assert len(error) > 1
    x = np.asarray(error,dtype=np.float)
    x = x[~np.isnan(x)]     #去除nan
    x = np.sort(x)          #排序
    n = len(x)              
    y = np.arange(1,n+1)/n  #返回1/n步进到1
    notdup = [x[i]-x[i-1]>0 for i in range(1,len(x))]  #返回梯度布尔值
    notdup.append(True) 
    xx = x[notdup]          #去除重复元素
    yy = np.insert(y[notdup],0,0) #在第一位置上插入一个0
    m = np.repeat(np.arange(len(xx)),2)  #在第0轴上复制元素
    xCDF = np.array([-np.inf,*xx[m],np.inf]) #前后延申
    yCDF = np.array([0,0,*yy[m]]) #在第一位置上插入两个0
    
    plt.plot(xCDF,yCDF)  #绘图
    plt.title(title)
    plt.xlabel("Position error")
    plt.ylabel("CDF")

    if savepath != ...:
        plt.savefig(savepath)
    if showfig:
        plt.show()
    return xCDF,yCDF

