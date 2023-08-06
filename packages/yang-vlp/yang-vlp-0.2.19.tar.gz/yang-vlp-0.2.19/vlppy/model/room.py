import os
import numpy as np
import pandas as pd
from typing import Sequence,Union
from numbers import Number
from ..error import VLPTypeError, VLPSequenceLenError, VLPValueError,VLPValueRangeError

class Room:
    """房间
    坐标系的建立:取房间后侧左下墙角为原点, 后侧左下墙角到前侧左下墙角为x轴方向,\
        后侧左下墙角到后侧右下墙角为y轴方向, 后侧左下墙角到后侧左上墙角为z轴方向
    """
    def __init__(self, 
                length:Number, 
                width:Number, 
                height:Number, 
                tp_gap:Union[Number,Sequence]=0.1,
                tp_height:Union[Number,Sequence]=0,
                reflect_wall:Sequence=[], 
                wall_gap:Union[Number,Sequence]=0.1,
                rho:Union[Number,Sequence]=0.5,
                *args,
                **kwargs) -> None:
        """房间大小
        length: 长
        width: 宽
        height: 高
        tp_gap: 测试区域划分网格的间隔  
        tp_height:测试区域距离地面的高度(默认取地面),也可以取[h0,h1]的一个高度范围
        reflect_wall: 存储反射墙壁序列号的列表(0=地面、1-4=前右后左、5=天花板) (在考虑墙壁有反射的情况下,使用该参数)
        wall_gap: 墙壁划分网格的间隔 (在考虑墙壁有反射的情况下,使用该参数)
        rho: 墙壁反射率 (在考虑墙壁有反射的情况下,使用该参数)
        """
        self.length = length #房间长
        self.width = width  #房间宽
        self.height = height  #房间高
        self.size = (length, width, height) #房间大小
        self.tp_gap = tp_gap  # 测试点平面划分网格的间隔
        self.tp_height = tp_height  # 测试区域距离地面的高度

        # 在考虑墙壁有反射的情况下，使用以下参数
        self.reflect_wall = reflect_wall  #存储反射墙壁序列号的集合
        self.wall_gap = wall_gap #墙壁划分网格的间隔
        self.rho = rho #墙壁反射率
        
        self.rp_height = [0, height]   # 前后左右反射墙壁高度范围

        self.origin = (0,0,0) #原点位置
        self.wall_args_path = f"wall_args.xlsx" # 默认墙壁参数地址

    def _get_reflect_wall_pos(self, gap, wall):
        """得到反射点坐标
        Params
            gap: 墙壁划分网格的间隔
            wall: 第几面墙(0=地板、1-4=前右后左、5=天花板)
        Return
            reflect_pos: 反射点坐标(列表元素个数等于反射单元的个数)
        """
        if wall not in (0,1,2,3,4,5):
            raise VLPValueError(wall,0,1,2,3,4,5)
        (xo, yo, zo) = self.origin # 原点
        gx, gy, gz = gap # 墙壁网格划分的间隔

        if wall in (0,5):    # 地板或天花板
            x = np.arange(gx, self.length-gx+1e-3, gx)  # 不取靠近墙壁的点（符合实际环境）
            y = np.arange(gy, self.width-gy+1e-3, gy) 
            z = 0 if wall == 0 else self.height 
            Xw, Yw, Zw = np.meshgrid(xo+x, yo+y, zo+z, indexing='ij') # 地板和天花板平面建立二维网格矩阵 
        elif wall in (1,3): #前后墙  
            x = np.arange(0, self.length+1e-3, gx) 
            y = 0 if wall == 1 else self.width 
            z = np.arange(self.rp_height[0], self.rp_height[1]+1e-3, gz) 
            Xw, Yw, Zw = np.meshgrid(xo+x, yo+y, zo+z, indexing='ij') # 前后墙面建立二维网格矩阵 
        else:  #左右墙
            x = self.length if wall == 2 else 0
            y = np.arange(0, self.width+1e-3, gy) 
            z = np.arange(self.rp_height[0], self.rp_height[1]+1e-3, gz) 
            Xw, Yw, Zw = np.meshgrid(xo+x, yo+y, zo+z, indexing='ij') # 左右墙面建立二维网格矩阵  
        Xw, Yw, Zw = Xw.flatten(), Yw.flatten(), Zw.flatten() # 打平
        reflect_pos = np.stack([Xw, Yw, Zw], axis=-1)
        return reflect_pos

    def _get_reflect_wall_angle(self, shape):
        """获取反射墙壁反射单元(法向量)的方位角和倾斜角
        Return 
            angles = [[alpha0,beta0],[alpha1,beta1],...] (列表元素个数等于反射单元的个数)
                alpha: 方位角(单位:度) (min,max) = (0°,360°)
                beta: 倾斜角(单位:度)  (min,max) = (-90°,90°)
        """
        alpha = np.random.uniform(low=0, high=360, size=shape)
        beta = np.random.uniform(low=-90, high=90, size=shape)
        angles = np.stack([alpha, beta], axis=-1)
        return angles

    def _save_reflect_wall_args(self, fp:str, reflect_pos, angles):
        """保存反射墙壁参数(方位角和倾斜角)到excell
        Params 
            fp: 保存路径
            reflect_pos: 墙壁反射单元所在位置
            angle: 获取墙壁反射单元角度(方位角和倾斜角)(单位:度)
        """
        if not np.shape(reflect_pos)[-1] == 3:
            raise VLPSequenceLenError(reflect_pos,3)
        if not np.shape(angles)[-1] == 2:
            raise VLPSequenceLenError(angles,2)
        xw, yw, zw = np.split(reflect_pos, indices_or_sections=3, axis=-1)  # 分割操作
        alpha, beta = np.split(angles, indices_or_sections=2, axis=-1) # 分割操作
        xw, yw, zw = xw.flatten(), yw.flatten(), zw.flatten() # 打平
        alpha, beta = alpha.flatten(), beta.flatten() # 打平
        wall_args = pd.DataFrame({
            "xw": xw,
            "yw": yw,
            "zw": zw,
            "alpha": alpha,
            "beta": beta
        })
        wall_args.to_excel(fp,index=False,header=True)
        # 保存为npz文件
        # np.savez(fp, alpha=alpha, beta=beta, xw=xw, yw=yw, zw=zw)
    
    def _load_reflect_wall_args(self, fp:str):
        """加载墙壁参数(方位角和倾斜角)到excell
        Params 
            fp: 文件路径
        Return
            reflect_pos,angles 反射单元坐标和反射单元角度(方向角和倾斜角)(单位:度)
        """
        wall_args = pd.read_excel(fp).to_numpy()
        xw, yw, zw, alpha, beta = np.split(wall_args,indices_or_sections=5,axis=-1)
        # 加载npz文件
        # with np.load(fp) as f:
        #     xw,yw,zw,alpha,beta = f['xw'],f['yw'],f['zw'],f['alpha'],f['beta']
        xw, yw, zw = xw.flatten(), yw.flatten(), zw.flatten() # 打平操作
        alpha, beta = alpha.flatten(), beta.flatten()
        reflect_pos = np.stack([xw, yw, zw], axis=-1)
        angles = np.stack([alpha, beta], axis=-1)
        return reflect_pos, angles

    def set_regular_wall(self):
        """设置为规制墙壁 (更新墙壁参数)
        """
        # 如果前后左右墙反射单元距离地面最小高度不为0,则无需考虑地面反射
        if self.rp_height[0] > 0 and 0 in self.reflect_wall:
            self.reflect_wall.remove(0)
        # 如果前后左右墙反射单元与天花板最小距离不为0,则无需考虑天花板反射
        if self.rp_height[1] < self.height and 5 in self.reflect_wall:
            self.reflect_wall.remove(5)

        for wall in self.reflect_wall:
            reflect_pos = self._get_reflect_wall_pos(self.wall_gap, wall) #得到反射点位置
            xw, _, _ = np.split(reflect_pos,indices_or_sections=3,axis=-1)
            shape = xw.flatten().shape # 打平后获取形状
            fpath = self.wall_args_path.format(wall) #默认路径
            alpha, beta = np.zeros(shape=shape), np.zeros(shape=shape)#获取墙壁参数(倾斜角和方向角)
            angles = np.stack([alpha, beta], axis=-1)
            self._save_reflect_wall_args(fpath, reflect_pos, angles) #保存墙壁参数

    def get_reflect_wall_args(self) -> list:
        """获取墙壁参数
        params
            无
        Return
            [(reflect_pos, angles),...]: 
                    反射墙壁网格坐标矩阵和反射单元角度(方向角和倾斜角) (列表元素个数等于反射墙壁的个数)
        """
        # 如果前后左右墙反射单元距离地面最小高度不为0,则无需考虑地面反射
        if self.rp_height[0] > 0 and 0 in self.reflect_wall:
            self.reflect_wall.remove(0)
            self.Aw.remove(self.reflect_wall.index(0))
        # 如果前后左右墙反射单元与天花板最小距离不为0,则无需考虑天花板反射
        if self.rp_height[1] < self.height and 5 in self.reflect_wall:
            self.reflect_wall.remove(5)
            self.Aw.remove(self.reflect_wall.index(5))

        reflect_wall_args = []  # 反射墙壁网格坐标和反射单元角度
        for wall in self.reflect_wall:
            reflect_pos = self._get_reflect_wall_pos(self.wall_gap, wall) #得到反射点位置
            pos_shape = np.shape(reflect_pos)

            fpath = self.wall_args_path.format(wall) #默认路径
            angles = None
            try:
                _,angles = self._load_reflect_wall_args(fpath) #加载墙壁参数
                assert pos_shape[0] == np.shape(angles)[0]  # 验证房间尺寸或墙壁划分间隔发生变化
            except FileNotFoundError as e:
                print(f"未发现反射墙壁{wall}参数文件!")
                print(f"随机生成反射墙壁{wall}参数保存到文件!")
                angles = self._get_reflect_wall_angle(shape=pos_shape[0]) #获取墙壁参数(倾斜角和方向角)
                self._save_reflect_wall_args(fpath, reflect_pos, angles) # 保存参数
            except AssertionError as e:
                print("房间尺寸或墙壁划分间隔发生变化!") # 会导致reshape失败
                print(f"重新生成反射墙壁{wall}参数文件!")
                angles = self._get_reflect_wall_angle(shape=pos_shape[0]) #获取墙壁参数(倾斜角和方向角)
                self._save_reflect_wall_args(fpath, reflect_pos, angles) # 保存参数
            else:
                print(f"反射墙壁{wall}参数文件加载成功!")
            finally:
                reflect_wall_args.append((reflect_pos, angles))
        return reflect_wall_args

    @property
    def length(self):
        """获取房间长度
        """
        return self._length

    @length.setter
    def length(self, l):
        """设置房间长度
        """
        self._length = l

    @property
    def width(self):
        """获取房间宽度
        """
        return self._width 

    @width.setter
    def width(self, w):
        """设置房间宽度
        """
        self._width = w

    @property
    def height(self):
        """获取房间高度
        """
        return self._height

    @height.setter
    def height(self, h):
        """设置房间高度
        """
        self._height = h

    @property
    def size(self) -> tuple:
        """获取房间大小
        """
        return (self.length, self.width, self.height)

    @size.setter
    def size(self, s:tuple):
        """设置房间大小
        """
        if not len(s) == 3:
            raise VLPSequenceLenError(s,3)
        self.length, self.width, self.height = s

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
            raise VLPSequenceLenError(o,3)
        self._origin = tuple(o)

    @property
    def tp_height(self):
        """获取测试区域高度范围
        """
        return self._tp_height
    
    @tp_height.setter
    def tp_height(self, h:Union[Number,Sequence]):
        """设置测试区域高度范围
        """
        if not isinstance(h,(Number, Sequence)): #类型
            raise VLPTypeError(h, Number, Sequence)
        if isinstance(h, Number): # 定位区域在房间中某一高度上（2D定位）
            assert 0 <= h <= self.height # 对取h的测试点平面高度限制
            h = np.full(shape=(2),fill_value=h) # 填充
        else:
            h = np.array(h)
            assert h.size == 2 and 0 <= h[0] <= h[1] <= self.height # 对取[h1,h2]的一个高度范围限制（3D定位）
        self._tp_height = h

    @property
    def tp_gap(self):
        """获取测试区域划分网格的间隔
        """
        return self._tp_gap
    
    @tp_gap.setter
    def tp_gap(self, gap:Union[Number, Sequence]):
        """设置测试区域划分网格的间隔
        """
        if not isinstance(gap,(Number ,Sequence)): #类型
            raise VLPTypeError(gap, Number, Sequence)

        # 测试点平面划分网格的间隔限制
        gap = np.asarray(gap)
        if not gap.size in (1,3):
            raise VLPValueError(gap.size,1,3)
        if not np.all((gap>0) & (gap<self.size)):
            raise VLPValueRangeError(gap, 0, self.size) # The gap setting is not reasonable!
        if gap.size == 1:
            gap = np.full(shape=(3), fill_value=gap) # 填充
        self._tp_gap = gap

    @property
    def tp_grid(self) -> tuple:
        """获取测试点位置的网格矩阵(所有测试点的相对位置)
        """
        (xo, yo, zo) = self._origin #原点位置

        gx, gy, gz = self.tp_gap # 测试区域划分网格的间隔
        tp_h1, tp_h2 = self.tp_height # 测试区域高度
        x = np.arange(0, self.length+1e-3, gx) # 房间长度等间隔划分的数组
        y = np.arange(0, self.width+1e-3, gy)  # 房间宽度等间隔划分的数组
        z = np.arange(tp_h1, tp_h2+1e-3, gz)   # 测试平面高度等间隔划分的数组
        xr, yr, zr = np.meshgrid(xo+x, yo+y, zo+z, indexing='ij') # 返回二维网格矩阵（测试点的相对位置）
        return xr.squeeze(), yr.squeeze(), zr.squeeze() 

    @property
    def tp_pos(self) -> tuple:
        """获取测试点位置
        """
        xr, yr, zr = self.tp_grid
        pos = np.stack([xr,yr,zr], axis=-1)
        return pos

    @property
    def tp_raw_pos(self) -> tuple:
        """获取测试点位置
            shape:(l*w*h)、(l*w*h)、(l*w*h)
        """
        xr, yr, zr = self.tp_grid
        xr, yr, zr = xr.flatten(), yr.flatten(), zr.flatten()
        return (xr, yr, zr) 

    @property
    def wall_gap(self):
        """获取墙壁划分网格的间隔 
        """
        return self._wall_gap
    
    @wall_gap.setter
    def wall_gap(self, gap:Union[Number, Sequence]):
        """设置墙壁划分网格的间隔
        """
        if not isinstance(gap,(Number, Sequence)): #类型
            raise VLPTypeError(gap, Number, Sequence)
        gap = np.asarray(gap)
        if not gap.size in (1,3):
            raise VLPValueError(gap.size,1,3)
        # 墙壁划分反射单元网格的间隔限制
        if not np.all((gap>0) & (gap<self.size)):
            raise VLPValueRangeError(gap, 0, self.size) # The gap setting is not reasonable!
        if gap.size == 1:
            gap = np.full(shape=(3), fill_value=gap)
        self._wall_gap = gap 

    @property
    def reflect_wall(self) -> list:
        """获取存储反射墙壁序列号的列表
        """
        reflect_wall = set(self._reflect_wall) #去除重复元素
        return np.array(list(reflect_wall))
    
    @reflect_wall.setter
    def reflect_wall(self, wall:Sequence):
        """设置存储反射墙壁序列号的列表
        """
        self._reflect_wall = wall

    @property
    def rho(self):
        """获取墙壁反射率
        """
        return self._rho
    
    @rho.setter
    def rho(self, n:Union[Number, Sequence]):
        """设置墙壁反射率
        """
        if not isinstance(n, (Number, Sequence)): #类型
            raise VLPTypeError(n, Number, Sequence)
        n = np.asarray(n)
        if not n.size in (1, self.reflect_wall.size): # 实际反射墙壁个数与反射面折射率个数需相等或全部相同
            raise VLPValueError(n.size, 1, self.reflect_wall.size)
        if n.size == 1:
            n = np.full(shape=(self.reflect_wall.size), fill_value=n) # 填充
        self._rho = n

    @property
    def Aw(self):
        """获取墙壁反射单元面积
        """
        gx, gy, gz = self.wall_gap # 墙壁网格划分的间隔(x,y,z轴方向)
        self._Aw = []
        for wall in self.reflect_wall:
            if wall in (0,5):  # 地板或天花板
                self._Aw.append(gx * gy) 
            elif wall in (1,3): # 前后墙
                self._Aw.append(gx * gz)
            else:  # 左右墙
                self._Aw.append(gy * gz) 
        return self._Aw

    @property
    def rp_height(self):
        """获取前后左右墙反射面距离地面高度范围
        """
        return self._rp_height
    
    def rp_height(self, h:Sequence):
        """设置前后左右墙反射面距离地面高度范围
        """
        if not isinstance(h, Sequence):
            raise VLPTypeError(h, Sequence)
        if not len(h) == 2:
            raise VLPSequenceLenError(h,2)
        assert 0 <= h[0] <= h[1] <= self.height # 对取h的反射面距离地面高度限制
        self._rp_height = h

    @property
    def wall_args_path(self):
        """获取墙壁参数保存地址
        """
        (filename,ext) = os.path.splitext(self._wall_args_path) # 分割文件名和后缀名
        fp = filename+'{}'+ext
        return fp
    
    @wall_args_path.setter
    def wall_args_path(self, fp:str):
        """设置墙壁参数保存地址
        """
        self._wall_args_path = fp

