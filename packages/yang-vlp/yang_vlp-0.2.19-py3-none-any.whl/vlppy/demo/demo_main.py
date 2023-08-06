import numpy as np
from ..setting import Settings
from ..io import IO
from .vlp_model import VLP_Model

Args = Settings() #加载settings.json文件
io = IO()  # 读写文件

save_excel_path = f'vlp_data.xlsx'
save_npz_path = f'vlp_data.npz'

def main():
    print("This is a demo about Visible light positioning!")
    print("In the LOS link, one LED acts as the transmitter, which transmits the DC signal, and four PDs are the receivers!")
    # 训练集
    cm = VLP_Model(**Args.items)
    (P1,P2,P3,P4,X,Y,Z) = cm.get_data()

    P_SUM = P1 + P2 + P3 + P4
    P = P_SUM
    cm.show(P)

    # 构建训练集
    train_in = np.stack([P1,P2,P3,P4],axis=-1)
    train_out = np.stack((X,Y,Z),axis=-1)

    train_dataset = {
        "P1": P1,
        "P2": P2,
        "P3": P3,
        "P4": P4,
        "X": X,
        "Y": Y,
        "Z": Z
    }

    # 训练集
    Args.items['Room']["test_plane"]["gap"] = 0.24  
    cm = VLP_Model(**Args.items)  
    (P1,P2,P3,P4,X,Y,Z) = cm.get_data()  

    P_SUM = P1 + P2 + P3 + P4
    P = P_SUM
    cm.show(P)

    # 构建测试集
    test_in = np.stack([P1,P2,P3,P4],axis=-1)
    test_out = np.stack((X,Y,Z),axis=-1)  

    test_dataset = {
        "P1": P1,
        "P2": P2,
        "P3": P3,
        "P4": P4,
        "X": X,
        "Y": Y,
        "Z": Z
    } 

    io.dataset_save_npz(save_npz_path,train_inputs=train_in,train_outputs=train_out,
                                    test_inputs=test_in,test_outputs=test_out)

    io.save_excel(save_excel_path, train_dataset, test_dataset)   


def test_func():
    """检验数据正确性
    """
    print("\nStatistics dataset:")
    print("*"*98)
    (train_inputs, train_outputs), (test_inputs, test_outputs) = io.dataset_load_npz(save_npz_path)
    print(f"train_inputs\t train_outputs\t test_inputs\t test_outputs")
    print(f"{train_inputs.shape}\t {train_outputs.shape}\t {test_inputs.shape}\t {test_outputs.shape}")
    print("train_inputs[:2]:\n",train_inputs[:2],"\ntrain_outputs[:2]:\n",train_outputs[:2])
    print("test_inputs[:2]:\n" ,test_inputs[:2],"\ntest_outputs[:2]:\n",test_outputs[:2])
    print(f"train_inputs: max value = {np.max(train_inputs)},\tmin value = {np.min(train_inputs)}")
    print(f"test_inputs : max value = {np.max(test_inputs)},\tmin value = {np.min(test_inputs)}")
    print("*"*98)

if __name__ == '__main__':
    for a in range(0,1):
        if a == 0:   # 产生数据
            main()
        elif a == 1: # 加载数据 验证数据集
            test_func()

