import numpy as np
from typing import Union
from ..error import VLPSequenceLenError,VLPValueError
from numbers import Number

class LED:
    """发光二极管
    """
    def __init__(self,
                theta:Number=30,
                pos:tuple=(0,0,0),
                Nv:tuple=(0,0,-1),
                signal:str="None",
                *args,
                **kwargs) -> None:
        """
        theta: LED半功率点半角 (单位: 度)
        pos: LED参考位置 (注意:self.pos设置的是参考位置,self.pos获取的是相对位置)
        Nv: LED法向量
        signal: LED发射信号类型
        *args和**kwargs:
            signal="None":无发射信号,无需传参数: 默认led.signal=0
            signal="DC":发射直流功率,传参详见函数: DC_Power(Pt);
            signal="AC":发射交流信号(电压信号或电流信号),传参详见函数: AC_Signal(DCbias, Amp, freq, t, signal_func);
            signal="AIM":强度调制功率信号,传参详见函数: AIM_Signal(Pt, m, freq, t, signal_func)
        """
        self.theta = theta
        self.pos = pos #参考位置
        self.Nv = Nv
        self.send_signal(signal,*args,**kwargs) 
        self.origin = (0,0,0) # 原点

    def DC_Signal(self, Pt, *args, **kwargs):
        """直流信号
        Params
            Pt: 直流功率
        Return 
            直流功率
        """
        return Pt

    @staticmethod
    def get_time_series(fs, npt):
        """获取时间序列
        Params
            fs: 采样率
            npt: 采样点数
        Return 
            t:时间序列
        """
        return np.arange(npt) / fs 

    def AC_Signal(self, DCbias, Amp, freq, t, signal_func:Union[str,np.ufunc]='cos', *args, **kwargs):
        """交流信号
        Params
            DCbias: 直流偏置
            Amp: 交流信号幅值
            freq: 交流信号频率
            t: 时间序列
            signal_func: 交流信号函数('sin', 'cos')
        Return 
            电压或电流信号
        """
        if signal_func not in ('sin', 'cos', np.sin, np.cos):
            raise VLPValueError(signal_func, 'sin', 'cos', np.sin, np.cos)
        if isinstance(signal_func, str):
            signal_func = np.sin if signal_func == 'sin' else np.cos
        t = np.array(t)   #时间序列 (npt)
        return DCbias + Amp * signal_func(2 * np.pi * (t * freq + np.random.random())) #交流信号 (npt)

    def AIM_Signal(self, Pt, m, freq, t, signal_func:Union[str,np.ufunc]='cos', *args, **kwargs):
        """强度调制
        Params
            Pt: 功率信号
            m: 调制指数
            freq: 调制信号频率
            t:时间序列
        Return 
            已调制信号
        """
        if signal_func not in ('sin', 'cos', np.sin, np.cos):
            raise VLPValueError(signal_func, 'sin', 'cos', np.sin, np.cos)
        if isinstance(signal_func, str):
            signal_func = np.sin if signal_func == 'sin' else np.cos
        return Pt*(1 + m*signal_func(2 * np.pi * (t * freq + np.random.random())))

    def send_signal(self, signal:str, *args, **kwargs):
        """设置内置的LED发射信号
        Params
            signal: LED信号类型
            *args和**kwargs:
                signal="None":无发射信号,无需传参: 默认led.signal=0;
                signal="DC":发射直流功率,传参详见函数: DC_Power(Pt);
                signal="AC":发射交流信号(电压信号或电流信号),传参详见函数: AC_Signal(DCbias, Amp, freq, t, signal_func);
                signal="AIM":强度调制功率信号,传参详见函数: AIM_Signal(Pt, m, freq, t, signal_func)
        Return
            无
        """
        print("led signal type:", signal)
        if signal not in ('None', 'DC', 'AC', 'AIM'):
            raise VLPValueError('None', 'DC', 'AC', 'AIM')

        if signal == 'DC':    # 直流功率
            self.signal = self.DC_Signal(*args,**kwargs)
        elif signal == 'AC':  # 交流信号
            self.signal = self.AC_Signal(*args,**kwargs)
        elif signal == 'AIM': # 强度调制
            self.signal = self.AIM_Signal(*args,**kwargs)
        else:   # 无发射信号
            self.signal = 0

    @property
    def signal(self):
        """获取LED发射的信号
        """
        return self._signal

    @signal.setter
    def signal(self, s):
        """注册LED发射的信号
        """
        self._signal = s

    @property
    def origin(self) -> tuple:
        """获取原点
        """
        return self._origin

    @origin.setter
    def origin(self, o):
        """设置原点
        """
        if not len(o) == 3:
            raise VLPSequenceLenError(o, 3)
        self._origin = tuple(o)

    @property
    def pos(self) -> tuple:
        """获取相对位置(参考位置相对与原点的相对位置)
        """
        return self._pos + self.origin
    
    @pos.setter
    def pos(self, pos:tuple):
        """设置参考位置
        """
        pos = np.asarray(pos)
        assert len(pos) == 3 or pos.shape[-1] == 3
        if len(pos) == 3:
            xr,yr,zr = pos
            pos = np.stack([xr,yr,zr], axis=-1)
        self._pos = pos # (3)
        
    @property
    def Nv(self):  
        """获取LED法向量  
        """  
        return self._Nv

    @Nv.setter
    def Nv(self, n): 
        """设置LED法向量 
        """
        N = np.asarray(n)
        assert len(n) == 3 or n.shape[-1] == 3
        if len(n) == 3:
            Nx,Ny,Nz = N
            N = np.stack([Nx,Ny,Nz], axis=-1)
        self._Nv = N

    @property
    def theta(self):  
        """获取半功率点半角 (单位: 度)  
        """  
        return self._theta

    @theta.setter
    def theta(self, t): 
        """设置半功率点半角 (单位: 度)  
        """
        self._theta = t

    @property
    def m(self):
        """获取朗伯发射级数 
        """
        theta_rad = np.radians(self.theta) # 角度制转弧度制
        return -np.log(2)/np.log(np.cos(theta_rad))
