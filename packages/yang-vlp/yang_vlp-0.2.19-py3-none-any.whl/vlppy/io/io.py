import scipy.io as scio
import pandas as pd
import numpy as np


class IO:
    """数据保存和读写
    """
    def save_excel(self, fp:str, *data, header=False,index=False):
        """保存为.excel
        加载:pd.read_excel(fp,sheet_name=Sheet1)  
        header: 是否包含标题
        index: 是否包含索引号（第一列行号）
        """
        dataset = []
        for dat in data:
            dataset.append(pd.DataFrame(dat))
        with pd.ExcelWriter(fp) as xlsx:
            for i,data in enumerate(dataset):
                data.to_excel(xlsx,'Sheet%d'%(i+1),header=header,index=index)

    def load_excel(self, fp:str, sheet:str="Sheet1", header=False):
        """加载excel,返回numpy类型数据
        """
        header = header if header else None 
        # 读取excell数据
        return pd.read_excel(fp,sheet_name=sheet,header=header).to_numpy()  

    def save_npz(self, fp:str, *data:dict):
        """保存为.npz
        加载:np.load(fp) 
        """
        dataset = {}
        for dat in data:
            dataset.update(dat)
        np.savez(fp, **dataset)
 
    def load_npz(self, fp, **argkeys):
        """加载numpy数据
        """
        return np.load(fp, **argkeys)

    def save_csv(self, fp:str, *dataFrame:dict):
        """保存为.csv
        加载:pd.read_csv(fp)
        """
        data = pd.DataFrame(data)
        data.to_csv(fp) 

    def load_csv(self, fp:str):
        """加载.csv文件
        """
        return pd.read_csv(fp).to_numpy()

    def svae_txt(self, fp:str, data:dict):
        """保存为.txt
        加载:np.loadtxt(fp) 
        """
        data = pd.DataFrame(data)
        np.savetxt(fp, data)
   
    # 读取txt 存储的数据
    def load_txt(self, fp:str, sep=None, start_row=0, end_row=-1, start_column=0, end_column=-1):
        return pd.read_csv(fp," ")

    def save_mat(self, fp:str, mdict:dict={}):
        """保存为.mat文件
        加载: scipy.io.loadmat(fp)
        """
        scio.savemat(fp, mdict)

    def load_mat(self, fp:str, keys:dict={}, default=None):
        """加载.mat文件
        """
        mdict = scio.loadmat(fp)
        output = []
        for key in keys:
            output.append(mdict.get(key, default))
        return output

    def user_save_npz_2d(self, fp:str, train_p=None, train_x=None, train_y=None, test_p=None, test_x=None, test_y=None):
        """用户保存numpy数据2D
        加载: user_load_npz_2d(fp)
        """
        # 数据保存.npz
        np.savez(fp,train_p=train_p,train_x=train_x,train_y=train_y,
                                test_p=test_p,test_x=test_x,test_y=test_y)

    def user_load_npz_2d(self, fp:str):
        """用户加载numpy数据2D
        """
        with np.load(fp) as f:
            train_p,train_x,train_y = f['train_p'],f['train_x'],f['train_y']
            test_p,test_x,test_y = f['test_p'],f['test_x'],f['test_y']
        return (train_p,train_x,train_y), (test_p,test_x,test_y)

    def user_save_npz_3d(self, fp:str, train_p=None, train_x=None, train_y=None, train_z=None, test_p=None, test_x=None, test_y=None, test_z=None):
        """用户保存numpy数据3D
        加载: user_load_npz_3d(fp)
        """
        # 数据保存.npz
        np.savez(fp, train_p=train_p, train_x=train_x, train_y=train_y, train_z=train_z,
                            test_p=test_p, test_x=test_x, test_y=test_y, test_z=test_z)

    def user_load_npz_3d(self, fp:str):
        """用户加载numpy数据3D
        """
        with np.load(fp) as f:
            train_p, train_x, train_y, train_z = f['train_p'], f['train_x'], f['train_y'], f['train_z']
            test_p, test_x, test_y, test_z = f['test_p'], f['test_x'], f['test_y'], f['test_z']
        return (train_p,train_x,train_y,train_z), (test_p,test_x,test_y,test_z)

    def dataset_save_npz(self, fp:str, train_inputs=None, train_outputs=None, test_inputs=None, test_outputs=None):
        """保存数据集
        加载: dataset_load_npz(fp)
        """
        np.savez(fp, train_inputs=train_inputs, train_outputs=train_outputs, 
                        test_inputs=test_inputs, test_outputs=test_outputs)

    def dataset_load_npz(self, fp:str):
        """加载数据集
        """
        with np.load(fp, allow_pickle=True) as f:
            train_inputs, train_outputs = f['train_inputs'], f['train_outputs'] 
            test_inputs, test_outputs = f['test_inputs'], f['test_outputs']
        return (train_inputs, train_outputs), (test_inputs, test_outputs)
    

    def data_sort(self, sfp:str, dfp: str="", column=0):
        """excel、csv数据排序(将excel中数据按某一列数据进行排序)
        Params
            sfp: 源地址
            dfp: 目标地址
            column: 第几列
        Return
            无
        """
        assert isinstance(column,int) and column >= 0
        if not dfp:
            (filename,ext) = sfp.split('.')
            dfp = filename+'1'+ext
        data = pd.read_excel(sfp)
        z = data.iloc[:,column].to_numpy()
        sort_z = np.argsort(z,kind='mergesort')
        sort_data = data.reindex(index=sort_z)
        sort_data.to_excel(dfp)

