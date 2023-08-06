@start date:  2022-08-26

@auther:  yangwuju

@url：https://gitee.com/yangwuju/yang_vlp

@file:

- model/room：房间、墙壁参数
- model/led：led位置、发射的信号(None、DC、AC、AIM)
- model/pd：pd 各种参数、LOS链路和NLOS链路接收LED信号、噪声
- signal/filter：滤波器设计（包括fir,iir）
- signal/plot：绘制波形图
- demo/vlp_model：可见光定位模型
- demo/demo_main：test demo
- io/io：数据保存与加载
- setting/json_setting：加载json配置文件
- error/error：VLP常见异常
- vis/vis：可视化绘图
- tools/decorator：VLP可能用到的装饰器

@download

```
py -m pip install yang-vlp
```

@updata log

静态定位（version=0.2.x）；

将测试平面更新为测试空间区域，可以实现3d定位仿真;

优化部分代码；
