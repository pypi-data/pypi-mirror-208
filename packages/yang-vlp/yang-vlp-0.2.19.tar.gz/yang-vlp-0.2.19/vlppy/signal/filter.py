import typing
from scipy import signal
import numpy as np
import matplotlib.pyplot as plt
from ..error import VLPValueError


class BandFilter:
    def __init__(self, n, fs, fm, w=2, *args, **kwargs) -> None:
        """理想带通滤波器
        n: 采样点数
        fs: 采样频率
        fm: 滤波器频率
        w: 通带到中心的距离 阻带为距离 w+Fd(频率间隔)
        """
        self.N = n # 采样点数
        self.Fs = fs # 采样频率
        self.T = 1/fs # 采样间隔
        self.t = np.arange(n) / fs # 时间序列
        self.fftfreq = np.fft.fftfreq(n,1/fs)  # 频率序列
        self.fm = fm  # 滤波频率
        self.W = w  # 通带宽度
        self.window_fft = self._window(w) # 窗函数
        self.window = np.fft.ifft(self.window_fft) # 窗函数的逆fft

    def _window(self, w):
        """
        # 窗函数(fft) lim:通带宽度
        """
        condition = (np.abs(self.fftfreq)>self.fm-w)&(np.abs(self.fftfreq)<self.fm+w)
        return np.where(condition,1,0)

    # 滤波
    def filter(self, signal):
        fft_signal = np.fft.fft(signal)
        fft_signal_filter = fft_signal * self.window_fft
        signal_filter = np.fft.ifft(fft_signal_filter)
        return signal_filter,fft_signal_filter

class BaseFilter:
    def __init__(self, fc, fs, D:list=[100,200], G:list=[2,35], btype='bandpass', analog=False, *args, **kwargs) -> None:
        """滤波器基类
        fc: 截止频率
        fs: 采样频率
        D:  [通带到中心的距离(单边通带宽度),阻带到中心的距离(单边阻带宽度)]
        G: 通带增益,阻带衰减
        btype: 滤波器类型,可选['lowpass', 'highpass', 'bandpass', 'bandstop']
        analog: 为True是模拟滤波器,为False是数字滤波器
        """
        if not btype in ['lowpass', 'highpass', 'bandpass', 'bandstop']:
            raise VLPValueError(btype, 'lowpass', 'highpass', 'bandpass', 'bandstop')

        self.Fc = fc # 滤波频率
        self.Fs = fs
        Pd,Sd = D[0],D[1]
        self.Wp = np.array([fc-Pd,fc+Pd])/(fs/2) # 通带频率 
        self.Ws = np.array([fc-Sd,fc+Sd])/(fs/2) # 阻带频率
        self.gp,self.gs = G[0],G[1]
        self.btype = btype
        self.analog = analog

    def show_wave(self, N, whole=False, savepath=..., showfig=True):
        """显示幅频响应波形、相频响应波形
        N: 采样点数
        whole: 单边还是全部
        """
        if self.analog:
            w,h = signal.freqs(self.b,self.a)
        else:
            w,h = signal.freqz(self.b,self.a,np.linspace(0, self.Fs if whole else self.Fs/2, N),whole=whole,fs=self.Fs) # 计算H(z)的幅频响应,freqz(b,a,计算点数,采样速率) 
        fig,ax = plt.subplots(2,1)
        ax[0].plot(w,20*np.log10(abs(h)))
        ax[0].set_xlabel('f:Hz')
        ax[0].set_ylabel('H:dB')
        ax[0].set_title('f-H') # 幅频响应波形
        # ax[0].set_ylim(-100,10)
        # angles = np.unwrap(np.angle(h))
        pha = np.angle(h) * 180 / np.pi
        ax[1].plot(w,pha)
        ax[1].set_xlabel('f:Hz')
        ax[1].set_ylabel('Pha:du')
        ax[1].set_title('f-Arc') # 相频响应波形
        if savepath != ...:
            plt.savefig(savepath)
        if showfig:
            plt.show()

    def filter(self, x, lfilter=False):
        """滤波
        x: 滤波信号
        lfilter: 为True使用lfilter滤波;为False使用filtfilt滤波
                 lfilter 滤波后的波形有偏移,filtfilt滤波后的没有偏移
        """
        return signal.lfilter(self.b,self.a,x) if lfilter else signal.filtfilt(self.b,self.a,x)

class ButterFilter(BaseFilter):
    def __init__(self, fc, fs, D:list=[100,200], G:list=[2,35], btype='bandpass', analog=False, *args, **kwargs) -> None:
        """巴特沃斯带通滤波器
        fc: 截止频率
        fs: 采样频率
        D: [通带到中心的距离(单边通带宽度),阻带到中心的距离(单边阻带宽度)]
        G: 通带增益,阻带衰减
        btype: 滤波器类型,可选['lowpass', 'highpass', 'bandpass', 'bandstop']
        analog: 为True是模拟滤波器,为False是数字滤波器
        """
        if not btype in ['lowpass', 'highpass', 'bandpass', 'bandstop']:
            raise VLPValueError(btype, 'lowpass', 'highpass', 'bandpass', 'bandstop')
        
        super(ButterFilter,self).__init__(fc,fs,D,G,btype,analog,*args,**kwargs)
        n, Wn = signal.buttord(self.Wp, self.Ws, self.gp, self.gs,analog=self.analog) # 返回巴特沃斯滤波器最小阶n和截止频率Wn
        self.b, self.a = signal.butter(n, Wn, btype='bandpass', analog=self.analog) # 返回归一化截止频率Wn的n阶巴特沃斯滤波器的传递函数系数

class ChebyFilter(BaseFilter):
    def __init__(self, fc, fs, D:list=[100,200], G:list=[2,35], btype='bandpass', analog=False, cheby=1, *args, **kwargs):
        """切比雪夫滤波器
        Params
            fc: 截止频率
            fs: 采样率
            D: [通带到中心的距离(单边通带宽度),阻带到中心的距离(单边阻带宽度)]
            G: 通带增益,阻带衰减
            btype: 滤波器类型,可选['lowpass', 'highpass', 'bandpass', 'bandstop']
            analog: 为True是模拟滤波器,为False是数字滤波器
            cheby: 为1时,为切比雪夫I型滤波器;为2时,为切比雪夫II型滤波器
        """
        if not btype in ['lowpass', 'highpass', 'bandpass', 'bandstop']:
            raise VLPValueError(btype, 'lowpass', 'highpass', 'bandpass', 'bandstop')
        if not cheby in [1,2]:
            raise VLPValueError(cheby, 1, 2)

        super(ChebyFilter,self).__init__(fc,fs,D,G,btype,analog,*args,**kwargs)
        if cheby == 1:
            ripple = self.gp
            filter_ord = signal.cheb1ord
            filter_func = signal.cheby1
        else:
            ripple = self.gs
            filter_ord = signal.cheb2ord
            filter_func = signal.cheby2

        n, Wn = filter_ord(self.Wp, self.Ws, self.gp, self.gs,analog=analog) # 返回滤波器最小阶n和截止频率Wn
        self.b, self.a = filter_func(n, ripple, Wn, btype=self.btype, analog=analog)

class EllipFilter(BaseFilter):
    def __init__(self, fc, fs, D:list=[100,200], G:list=[2,35], btype='bandpass', analog=False, *args, **kwargs) -> None:
        """椭圆滤波器
        fc: 截止频率
        fs: 采样频率
        D: [通带到中心的距离(单边通带宽度),阻带到中心的距离(单边阻带宽度)]
        G: 通带增益,阻带衰减
        btype: 滤波器类型,可选['lowpass', 'highpass', 'bandpass', 'bandstop']
        analog: 为True是模拟滤波器,为False是数字滤波器
        """
        if not btype in ['lowpass', 'highpass', 'bandpass', 'bandstop']:
            raise VLPValueError(btype, 'lowpass', 'highpass', 'bandpass', 'bandstop')
        super(EllipFilter,self).__init__(fc,fs,D,G,btype,analog,*args,**kwargs)

        n, Wn = signal.ellipord(self.Wp, self.Ws, self.gp, self.gs,analog=self.analog) # 返回巴特沃斯滤波器最小阶n和截止频率Wn
        rp,rs = self.gp,self.gs
        self.b, self.a = signal.ellip(n, rp, rs, Wn, btype=self.btype,analog=self.analog) # 返回归一化截止频率Wn的n阶巴特沃斯滤波器的传递函数系数

class BesselFilter(BaseFilter):
    def __init__(self, fc, fs, n, Wn:typing.Union[int,list], btype='bandpass', analog=False, *args, **kwargs) -> None:
        """贝塞尔滤波器
        fc: 截止频率
        fs: 采样频率
        n: 滤波器阶数
        wn: 单边通带宽度
        btype:滤波器类型,可选['lowpass', 'highpass', 'bandpass', 'bandstop']
        analog:为True是模拟滤波器,为False是数字滤波器
        """
        if not btype in ['lowpass', 'highpass', 'bandpass', 'bandstop']:
            raise VLPValueError(btype, 'lowpass', 'highpass', 'bandpass', 'bandstop')
        super(BesselFilter,self).__init__(fc,fs,btype=btype,analog=analog,*args,**kwargs)
        if np.array(Wn).size == 2:
            Wn = np.array([fc-Wn[0],fc+Wn[1]]) / (fs/2)
        else:
            Wn = Wn if btype in ['lowpass', 'highpass'] else np.array([fc-Wn,fc+Wn]) / (fs/2)
        self.b, self.a = signal.bessel(n, Wn, btype=self.btype,analog=self.analog) # 返回归一化截止频率Wn的n阶巴特沃斯滤波器的传递函数系数

class FIR_Filter(BaseFilter):
    def __init__(self, fc, fs, n, Wp, window='hamming', btype='bandpass', *args, **kwargs) -> None:
        """Fir滤波器
        Params
            fc:截止频率
            fs:采样率
            n:滤波器阶数(越大越好)
            Wp:单边通带宽度
            window:窗函数,可选["barthann","bartlett","blackman","blackmanharris","bohman","boxcar","chebwin","cosine",
                        "dpss","exponential","flattop""gaussian","general_cosine","general_gaussian","general_hamming",
                        "hamming","hann","hanning","kaiser","nuttall","parzen","taylor","triang","tukey"]
            btype:滤波器类型,可选[True, False,'lowpass', 'highpass', 'bandpass', 'bandstop']
        """
        if not btype in [True, False, 'lowpass', 'highpass', 'bandpass', 'bandstop']:
            raise VLPValueError(btype, 'lowpass', 'highpass', 'bandpass', 'bandstop')
        super(FIR_Filter,self).__init__(fc,fs,btype=btype,analog=False,*args,**kwargs)
        if np.array(Wp).size == 2:
            Wp = np.array([fc-Wp[0],fc+Wp[1]])/(fs/2)
        else:
            Wp = np.array([fc-Wp,fc+Wp])/(fs/2) if btype in ['bandpass', 'bandstop'] else Wp/ (fs/2) 
        # window = signal.windows.boxcar(n)
        # window = signal.get_window('boxcar',n)
        self.b, self.a = signal.firwin(n+1,Wp,window=window,pass_zero=btype), 1



