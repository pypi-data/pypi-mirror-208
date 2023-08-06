import numpy as np
import matplotlib.pyplot as plt
from typing import Union,Sequence

def signal_wave(x,
                *y,
                timeAxis=True,
                xlab:Union[str,Sequence]="",
                ylab:Union[str,Sequence]="",
                title:Union[str,Sequence]="",
                savepath=...,
                showfig=True):
    '''
    显示时域信号波形
    x:  当timeAxis为True时,x为时间序列
        当timeAxis为False时,x为频率序列
    *y: 当timeAxis为True时,*y为时域信号
        当timeAxis为False时,*y为频率信号
    timeAxis: 为True时x,*y传入时域信号
              为False时x,*y传入频域信号 
    xlab: x轴标签
    ylab: y轴标签
    title: 标题
    '''
    _len = len(y)
    if isinstance(xlab,str):
        xlab = [xlab for _ in range(_len)]
    if isinstance(ylab,str):
        ylab = [ylab for _ in range(_len)]
    if isinstance(title,str):
        title = [title for _ in range(_len)]
    if isinstance(xlab,Sequence):
        [xlab.append("") for _ in range(_len - len(xlab))]
    if isinstance(ylab,Sequence):
        [ylab.append("") for _ in range(_len - len(ylab))]
    if isinstance(title,Sequence):
        [title.append("") for _ in range(_len - len(title))]
    N = len(x)
    T = x[1]-x[0] if timeAxis else (x[1]-x[0])/N
    t = x if timeAxis else np.arange(N)*T # 时间序列
    fig,ax = plt.subplots(len(y),1,squeeze=False)
    for i,u in enumerate(y):
        U = u if timeAxis else np.fft.ifft(u)
        ax[i][0].plot(t,u)
        ax[i][0].set_title(title[i])
        ax[i][0].set_xlabel(xlab[i])
        ax[i][0].set_ylabel(ylab[i])
    
    if savepath != ...:
        plt.savefig(savepath)
    if showfig:
        plt.show()

def signal_fft_wave(x,
                    *y,
                    freqAxis:bool=False,
                    single:bool=True,
                    xlab:Union[str,Sequence]="",
                    ylab:Union[str,Sequence]="",
                    title:Union[str,Sequence]="",
                    savepath=...,
                    showfig=True):
    '''
    显示信号频域波形
    x:  当freqAxis为True时,x为频率序列
        当freqAxis为False时,x为时间序列
    *y: 当freqAxis为True时,*y为频率信号
        当freqAxis为False时,*y为时域信号
    freqAxis: 为True时x,*y传入频域信号
              为False时x,*y传入时域信号
    single: 指定是单边波形,还是双边波形
    xlab: x轴标签
    ylab: y轴标签
    title: 标题
    '''  
    _len = len(y)
    if isinstance(xlab,(str)):
        xlab = [xlab for _ in range(_len)]
    if isinstance(ylab,str):
        ylab = [ylab for _ in range(_len)]
    if isinstance(title,str):
        title = [title for _ in range(_len)]
    if isinstance(xlab,Sequence):
        [xlab.append("") for _ in range(_len - len(xlab))]
    if isinstance(ylab,Sequence):
        [ylab.append("") for _ in range(_len - len(ylab))]
    if isinstance(title,Sequence):
        [title.append("") for _ in range(_len - len(title))]
    N = len(x)
    T = (x[1]-x[0])/N if freqAxis else x[1]-x[0]  # 信号周期
    f = x if freqAxis else np.fft.fftfreq(N, T) # 信号频率
    fig,ax = plt.subplots(len(y),1,squeeze=False)
    for i,u in enumerate(y):
        U = u if freqAxis else np.fft.fft(u)
        ax[i][0].plot(f[:N//2],2.0/N * np.abs(U[0:N//2])) if single else ax[i][0].plot(f,U)
        ax[i][0].set_title(title[i])
        ax[i][0].set_xlabel(xlab[i])
        ax[i][0].set_ylabel(ylab[i])
 
    if savepath != ...:
        plt.savefig(savepath)
    if showfig:
        plt.show()
