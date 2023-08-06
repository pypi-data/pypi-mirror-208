import numpy as np
from numbers import Number
from typing import Union
from .led import LED
from .room import Room
from ..error import VLPSequenceLenError,VLPValueRangeError

class PD:
    """光电探测器
    """
    def __init__(self,
                n:Number=1.5,
                fov:Number=60,
                Ar:Number=1e-4,
                Ts:Number=1,
                pos:tuple=(0,0,0),
                Nv:tuple=(0,0,1),
                *args,
                **kwargs) -> None:
        """ 
        n: 透镜的折射率
        fov: 接收视场角 (单位: 度) [0,90]
        Ar: PD检测器的接收面积(单位:平方米)
        Ts: 光学滤波器的增益
        pos: PD参考位置(注意:self._pos为参考位置,self.pos为相对位置) 
        Nv: PD 法向量
        """
        self.n = n
        self.fov = fov
        self.Ar = Ar
        self.Ts = Ts

        self.pos = pos
        self.Nv = Nv
        self.origin = (0,0,0) #原点位置

    @staticmethod
    def recv_frame_model(l, alpha, beta, center_tp_pos:tuple):
        """接收机模型:PD支架模型(倾斜PD和中心参考点位置关系)
        Params
            l: 倾斜PD到中心水平PD(参考点)的长度(单位:米)
            alpha: PD摆放角(单位:度)
            beta: PD倾斜面倾斜角(单位:度)
            center_tp_pos: 水平中心测试点位置
        Return
            pos: 倾斜PD位置
            Nv: 倾斜PD的法向量
        """
        if len(center_tp_pos) == 3:
            x0, y0, z0 = center_tp_pos
        else:
            x0, y0, z0 = np.split(center_tp_pos, indices_or_sections=3, axis=-1)
        x0, y0, z0 = x0.flatten(), y0.flatten(), z0.flatten()

        # 角度制转弧度制
        alpha_rad, beta_rad = np.radians([alpha, beta])

        # 倾斜PD和中心参考点位置关系
        xr = x0 + l * np.cos(alpha_rad) * np.cos(beta_rad) 
        yr = y0 + l * np.sin(alpha_rad) * np.cos(beta_rad)
        zr = z0 + l * np.sin(beta_rad)
        
        # alpha_rad+np.pi: PD的方位角和PD倾斜面的摆放角反向
        # beta_rad: PD的法向量与z轴的夹角和PD倾斜面的倾斜角相等
        Nx = np.cos(alpha_rad+np.pi) * np.sin(beta_rad)
        Ny = np.sin(alpha_rad+np.pi) * np.sin(beta_rad)
        Nz = np.cos(beta_rad)

        if len(center_tp_pos) == 3:
            pos = (xr,yr,zr)
            Nv = (Nx,Ny,Nz)
        else:
            pos = np.stack([xr,yr,zr], axis=-1) # 在最后一维度上堆叠
            Nv = np.stack([Nx,Ny,Nz], axis=-1)
        
        return pos, Nv

    @staticmethod
    def recv_surface_model(r:Union[Number,tuple], alpha, beta, center_tp_pos:tuple):
        """接收机模型:安全帽椭球面(倾斜PD和中心参考点位置关系)
        Params
            r: 曲球面半径(单位:米)
            alpha: PD摆放角(单位:度)
            beta: 椭球球心与PD连线与z轴夹角(单位:度)
            center_tp_pos: 椭球面顶部中心测试点位置
        Return
            pos: 倾斜PD位置
            Nv: 倾斜PD的法向量
        """
        r = np.asarray(r)
        assert r.size in (1,3)
        a, b, c = np.full(shape=(3), fill_value=r) if r.size == 1 else r

        # 角度制转弧度制
        alpha_rad, beta_rad = np.radians([alpha,beta]) 

        if not 0 <= beta_rad <= 90: # 限定
            raise VLPValueRangeError(beta, 0, 90)
        
        if len(center_tp_pos) == 3:
            x0, y0, z0 = center_tp_pos
        else:
            x0, y0, z0 = np.split(center_tp_pos, indices_or_sections=3, axis=-1)
        x0, y0, z0 = x0.flatten(), y0.flatten(), z0.flatten()
        
        # 倾斜PD位置
        xr = x0 + a * np.cos(alpha_rad) * np.sin(beta_rad)
        yr = y0 + b * np.sin(alpha_rad) * np.sin(beta_rad)
        zr = z0 - c * (1 - np.cos(beta_rad))

        # alpha_rad: PD的方位角和PD倾斜面的摆放角相等
        # beta_rad: 椭球球心与PD连线与z轴夹角
        Nx = 1/a * np.cos(alpha_rad) * np.sin(beta_rad)
        Ny = 1/b * np.sin(alpha_rad) * np.sin(beta_rad)
        Nz = 1/c * np.cos(beta_rad)

        # PD位置与法向量
        if len(center_tp_pos) == 3:
            pos = (xr,yr,zr)
            Nv = (Nx,Ny,Nz)
        else:
            pos = np.stack([xr,yr,zr], axis=-1)
            Nv = np.stack([Nx,Ny,Nz], axis=-1)

        return pos, Nv

    @staticmethod
    def recv_hemisphere_model(r, l, alpha, center_tp_pos:tuple):
        """接收机模型:半球面模型(倾斜PD和中心参考点位置关系)
        Params
            r: 曲球面半径(单位:米)
            l: 倾斜PD到顶部中心(参考点)的弧长(单位:米)   
            alpha:倾斜PD方位角(单位:度) 
            center_tp_pos: 测试点位置 
        Return
            pos: 倾斜PD位置
            Nv: 倾斜PD的法向量
        """
        # 倾斜PD的方位角和倾斜角
        beta_rad = l/r   # 椭球球心与PD连线与z轴夹角(PD倾斜角)
        beta = np.degrees(beta_rad) # 弧度制转角度制
        pos, Nv = PD.recv_surface_model(r, alpha, beta, center_tp_pos)
        return pos, Nv

    def recv_led_radiation_intensity(self, led:LED):
        """计算LED辐射强度(LOS链路):
        Parameters
            led: LED实例化
        Return 
            LOS链路LED辐射强度
        """
        Vt_r = self.pos - led.pos                 # LED到PD的方向向量 (l*w*h,3)
        d = np.linalg.norm(Vt_r,axis=-1)          # LED到PD的方向向量的模 (l*w*h)
        led_Nv = led.Nv/np.linalg.norm(led.Nv)    # LED单位法向量
        cos_led_t_angle_rad_rad = np.sum(Vt_r*led_Nv, axis=-1) / d # LED发射角的余弦值 (l*w*h)

        R0 = ((led.m + 1)  / (2 * np.pi)) * cos_led_t_angle_rad_rad**led.m  # 辐射强度模型 (l*w*h)

        """
        H0 = H0.flatten() #打平 (l,w) -> (l*w,)
        return np.array([np.convolve(h,led.send_signal) for h in H0])  #卷积 (l*w,npt)
              <=> np.array([h * led.send_signal for h in H0])          #相乘 (l*w,npt) 
        """
        R0 = np.expand_dims(R0,-1) # 在最后一维扩充一个维度 (l*w*h) -> (l*w*h,1)  <=> H0.reshape(l*w*h,1) <=> H0[...,np.newaxis]
        radiation_intensity = R0 * led.signal # LED辐射强度[广播机制 (l*w*h,1) * (npt) -> (l*w*h,npt) * (l*w*h,npt) = (l*w*h,npt)]
        return np.squeeze(radiation_intensity)  # (l*w*h,npt).如果npt==1,则返回形状为(l*w*h)

    def recv_los_led_signal(self, led:LED):
        """计算PD接收LED信号(LOS链路):
        Parameters
            led: LED实例化
        Return 
            LOS链路中PD探测器接收LED信号
        """
        # LED发射端
        Vt_r = self.pos - led.pos                     # LED到PD的方向向量 (l*w*h,3)
        d = np.linalg.norm(Vt_r,axis=-1)              # 求模:LED到PD的方向向量的模 (l*w*h)
        led_Nv = led.Nv/np.linalg.norm(led.Nv)        # LED单位法向量
        cos_led_t_angle_rad_rad = np.sum(Vt_r*led_Nv, axis=-1) / d  # LED发射角的余弦值 (l*w*h)

        # PD接收端
        Vr_t = -Vt_r # PD到LED的方向向量 (l*w*h,3)
        pd_Nv = self.Nv/np.linalg.norm(self.Nv)                # PD单位法向量
        cos_pd_r_angle_rad = np.sum(Vr_t*pd_Nv, axis=-1) / d   # PD接收角的余弦值 (l*w*h) 

        # PD入射角
        pd_r_angle_rad = np.arccos(cos_pd_r_angle_rad) # PD接收器入射角的大小(弧度制) (l*w*h)
        pd_r_angle = np.degrees(pd_r_angle_rad)        # 弧度制转为角度制 (l*w*h)

        # 计算信道增益
        H0 = (((led.m + 1) * self.Ar) / (2 * np.pi * d**2)) * cos_led_t_angle_rad_rad**led.m * cos_pd_r_angle_rad * self.Ts * self.G_Con # 信道增益 (l*w*h)
        H0 = np.where((pd_r_angle>=0) & (pd_r_angle<=self.fov), H0, 0)  # 视场内信道增益 (l*w*h) <=> np.place(H0,(phi>=0)&(phi<=pd.fov),0)

        # 以下是为了兼容交直流信号
        """
        H0 = H0.flatten() #打平 (l,w) -> (l*w,)
        return np.array([np.convolve(h,led.send_signal) for h in H0])  #卷积 (l*w,npt)
              <=> np.array([h * led.send_signal for h in H0])          #相乘 (l*w,npt) 
        """
        H0 = np.expand_dims(H0,-1) # 在最后一维扩充一个维度 (l*w*h) -> (l*w*h,1)  <=> H0.reshape(l*w*h,1) <=> H0[...,np.newaxis]
        recv_signal = H0 * led.signal # PD接收信号 [广播机制 (l*w*h,1) * (npt) -> (l*w*h,npt) * (l*w*h,npt) = (l*w*h,npt)]
        return np.squeeze(recv_signal) # (l,w,h,npt).如果npt==1,则返回形状为(l,w,h)
      
    def recv_nlos_led_signal(self, led:LED, room:Room):
        """计算PD接收LED一次反射信号(NLOS链路):
        Params
            led: LED实例化
            room: Room实例化
        Return 
            NLOS链路中PD探测器接收LED一次反射信号
        """
        # 对PD坐标张量扩充维度,以便使用广播
        pd_pos = np.expand_dims(self.pos,axis=-2)  # (l*w*h,3) -> (l*w*h,1,3) 
        # print(f"{pd_pos.shape=}")

        H0 = 0  #反射（LOS）链路信道增益
        # 遍历每一面反射墙壁参数:(l1*w1,3),(l1*w1,2)
        for i, (w_pos, angle) in enumerate(room.get_reflect_wall_args()):
            w_alpha, w_beta = np.split(angle,indices_or_sections=2, axis=-1) # (l1*w1,2) -> (l1*w1,1) + (l1*w1,1)
            w_alpha, w_beta = w_alpha.flatten(), w_beta.flatten() # (l1*w1,1) -> (l1*w1)
            # 墙壁反射单元的方向角和倾斜角,角度制转弧度制
            w_alpha_rad, w_beta_rad = np.radians([w_alpha, w_beta]) # (l1*w1)

            # 墙壁反射单元法向量
            Nx = np.cos(w_alpha_rad) * np.sin(w_beta_rad)
            Ny = np.sin(w_alpha_rad) * np.sin(w_beta_rad)
            Nz = np.cos(w_beta_rad)
            Nw = np.stack([Nx,Ny,Nz], axis=-1)  # 墙壁反射点法向量 (l1*w1,3)
            Nw = Nw/np.linalg.norm(Nw)          # 墙壁反射点的单位法向量 (l1*w1,3)

            # LED -> 墙壁反射单元
            # 发射端
            Vt_w = w_pos - led.pos             # LED灯到墙壁反射单元的方向向量 (l1*w1,3)
            d1 = np.linalg.norm(Vt_w, axis=-1) # 求模:LED灯到墙壁反射单元的距离 (l1*w1)
            mark1 = np.all(Vt_w==0, axis=-1)   # 异常点处理:判断墙壁反射单元和LED是否重合(方向向量是否为零向量) (l1*w1)
            d1 = np.where(mark1, 1, d1)        # 异常点处理:为使cos_led_t_angle_rad分母不为0,让墙壁反射单元和LED重合时的距离不为0 (l1*w1)
            
            led_Nv = led.Nv/np.linalg.norm(led.Nv)        # LED单位法向量
            cos_led_t_angle_rad = np.sum(Vt_w*led_Nv, axis=-1) / d1  # LED发射角的余弦值 (l1*w1)

            # 接收端
            Vw_t = -Vt_w  # 墙壁反射单元到LED灯的方向向量 (l1,w1,3)
            cos_wall_r_angle_rad = np.sum(Vw_t*Nw, axis=-1) / d1 # 墙壁反射单元入射角 (l1*w1)

            # 墙壁反射单元 -> PD
            # 发射端
            Vw_r = pd_pos - w_pos # 墙壁反射单元到PD的方向向量  (l*w*h,1,3)-(l1*w1,3) (l*w*h,l1*w1,3)
            d2 = np.linalg.norm(Vw_r, axis=-1) # 求模:墙壁反射单元到PD之间的距离 (l*w*h,l1*w1)

            mark2 = np.all(Vw_r==0, axis=-1) # 异常点处理:判断墙壁反射单元和参考点是否重合(方向向量是否为零向量) (l*w*h,l1*w1)
            d2 = np.where(mark2, 1, d2)      # 异常点处理:为使cos_wall_t_angle_rad分母不为0,让墙壁反射单元和参考点重合时的距离不为0

            cos_wall_t_angle_rad = np.sum(Vw_r*Nw, axis=-1) / d2 # 墙壁反射单元发射角  (l*w*h,l1*w1)
            cos_wall_t_angle_rad = np.where(cos_wall_t_angle_rad>0, cos_wall_t_angle_rad, 0) # 满足墙壁反射入射条件 (l*w*h,l1*w1)
      
            # 接收端
            Vr_w = -Vw_r  # PD到墙壁反射单元的方向向量   (l*w*h,l1*w1,3)
            pd_Nv = self.Nv/np.linalg.norm(self.Nv)               # PD单位法向量
            cos_pd_r_angle_rad = np.sum(Vr_w*pd_Nv, axis=-1) / d2 # PD接收角的余弦值   (l*w*h,l1*w1)
            cos_pd_r_angle_rad = np.where(cos_pd_r_angle_rad>0, cos_pd_r_angle_rad, 0) # 满足墙壁反射发射条件

            # PD入射角
            pd_r_angle_rad = np.arccos(cos_pd_r_angle_rad) # PD接收器入射角(弧度制) (l*w*h,l1*w1)
            pd_r_angle = np.degrees(pd_r_angle_rad) # 弧度制转为角度制 (l*w*h,l1*w1)

            rho = room.rho[i]   #墙壁反射率
            Aw = room.Aw[i]     #墙壁反射单元面积

            # 反射(NLOS)子链路信道增益 (l,w,h,l1,w1)
            Hw = (((led.m + 1) * self.Ar) / (2 * np.pi**2 * d1**2 * d2**2)) * rho * Aw * cos_led_t_angle_rad**led.m * cos_wall_r_angle_rad * cos_wall_t_angle_rad *  cos_pd_r_angle_rad * self.Ts * self.G_Con  # 信道增益 
            Hw = np.where((pd_r_angle>=0) & (pd_r_angle<=self.fov), Hw, 0)  # 视场内信道增益 (l*w*h,l1*w1)

            Hw = np.sum(Hw, axis=-1)   # 反射(NLOS)链路信道增益求和 (l*w*h)
            H0 += Hw  # 墙壁反射(NLOS)链路信道增益(l*w*h)
        
        H0 = np.expand_dims(H0,-1) # 在最后一维扩充一个维度 (l*w*h) -> (l*w*h,1)  <=> H0.reshape(l*w*h,1) <=> H0[...,np.newaxis]
        recv_signal = H0 * led.signal # PD接收信号[广播机制 (l*w*h,1) * (npt) -> (l*w*h,npt) * (l*w*h,npt) = (l*w*h,npt)]
        return np.squeeze(recv_signal) # 去除维度为1的维数
    
    def recv_led_signal(self, led:LED, room:Room):
        """计算PD接收LED信号(LOS+NLOS链路):
        Params
            led: LED实例化
            room: Room实例化
        Return 
            LOS+NLOS链路中PD探测器接收LED信号
        """
        recv_los_signal = self.recv_los_led_signal(led=led)  # PD接收直射链路信号
        recv_nlos_signal = self.recv_nlos_led_signal(led=led, room=room) # PD接收一次反射链路信号
        return recv_los_signal + recv_nlos_signal

    def shot_noise(self, P, R=0.4, Ibg=5, I2=0.562, B=100, *argv, **kwargv):
        """获取PD散粒噪声功率
        Params
            P: PD接收功率(W)
            R: PD响应度(A/W)
            Ibg: 暗电流(uA)
            I2: 噪声带宽系数
            B: 噪声带宽(MHz)
        Return 
            PD散粒噪声功率
        """
        q = 1.6e-19  # 电子电荷量(C)
        # Ibg *= 1e-6  # 单位换算 （1 A = 1e6 uA）
        # B *= 1e6  
        return 2*q*R*P + 2*q*Ibg*I2*B
    
    def thermal_noise(self, Tk=300, G=10, eta=112, B=100, I2=0.562, I3=0.0868, gamma=1.5, gm=30, *argv, **kwargv):
        """获取PD热噪声功率
        Params
            Tk: 热力学温度:Tk = T + 273.15°C(K)
            G: 开环电压增益
            eta: PD每单位面积上固定电容(pF/cm2)
            B: 噪声带宽(MHz)
            I2: 噪声带宽系数 
            I3: 噪声带宽系数 
            gamma: 信道噪声系数
            gm: 跨导(m/S)
        Return
            PD热噪声功率
        """
        k = 1.38e-23  # 玻尔兹曼常数
        eta *= 1e-8 # 单位换算（1pF/cm2 = 1e-8F/m2）
        B *= 1e6
        gm *= 1e-3
        return 8*np.pi*k*Tk/G*eta*self.Ar*I2*B**2 + \
            16*np.pi**2*k*Tk*gamma/gm*eta**2*self.Ar**2*I3*B**3

    def recv_noise_signal(self, *argv, **kwargv):
        """接收噪声信号功率
        """
        return self.shot_noise(*argv, **kwargv) + self.thermal_noise(*argv, **kwargv)

    @property
    def origin(self) -> tuple:
        """设置原点位置
        """
        return self._origin

    @origin.setter
    def origin(self, o):
        """获取原点位置
        """
        if not len(o) == 3:
            raise VLPSequenceLenError(o,3)
        self._origin = tuple(o) 

    @property
    def pos(self):
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
        self._pos = pos # (L*w*h,3)

    @property
    def Nv(self):  
        """获取PD法向量  
        """  
        return self._Nv
    
    @Nv.setter
    def Nv(self, n):
        N = np.asarray(n)
        assert len(n) == 3 or n.shape[-1] == 3
        if len(n) == 3:
            Nx,Ny,Nz = N
            N = np.stack([Nx,Ny,Nz], axis=-1)
        self._Nv = N

    @property
    def fov(self):
        """获取接收视场角 (单位: 度)
        """    
        return self._fov

    @fov.setter
    def fov(self, fov): 
        """设置接收视场角 (单位: 度)
        """
        if not 0 <= fov <= 90:
            raise VLPValueRangeError(fov,0,90)
        self._fov = fov

    @property
    def Ar(self):   
        """获取PD检测器的接收面积(单位:平方米)
        """ 
        return self._Ar

    @Ar.setter
    def Ar(self, a): 
        """设置PD检测器的接收面积(单位:平方米)
        """
        self._Ar = a

    @property
    def Ts(self):   
        """获取光学滤波器的增益 
        """ 
        return self._Ts

    @Ts.setter
    def Ts(self, ts): 
        """设置光学滤波器的增益 
        """
        self._Ts = ts

    @property
    def n(self): 
        """获取透镜的折射率
        """   
        return self._n

    @n.setter
    def n(self, n): 
        """设置透镜的折射率
        """
        self._n = n

    @property
    def G_Con(self):
        """获取聚光器增益
        """
        fov_rad = np.radians(self.fov)
        return self.n**2 / np.sin(fov_rad)**2  

