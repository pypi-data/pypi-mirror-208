# -*- coding: utf-8 -*-
# @Time : 2023/5/14 9:45
# @Author : zhao
# @Email : liming7887@qq.com
# @File : convNetWork.py
# @Project : ZWell-model
import zWell_model.utils as zu
from zWell_model.allModel import AllModel


class ConvNet(AllModel):
    """
    最基本的卷积神经网络结构类
    """

    def __init__(self, stride, input_shape, classes,
                 model_layers_num=1, ckp=2, init_k_len=64, dense_len=512):
        """
        构造出来一个卷积神经网络对象
        :param stride: 每一个残差块的卷积步长 需要注意的是，这是一个list，作为每一个残差块的卷积步长。
        :param input_shape: 残差神经网络的输入维度元组
        :param classes: 残差神经网络的分类方式
        :param model_layers_num: 残差神经网络层数量
        :param ckp: 卷积层之间的卷积核数量等比数值
        :param init_k_len 第一层残差块中的卷积核数量
        :param dense_len 残差结束之后，全连接神经元第一层的神经元数量
        """
        super().__init__()
        # 检查步长 并 赋值步长
        zu.check_list_len(stride, model_layers_num, "Convolutional step size for each residual block:[stride]")
        self.input_shape = input_shape
        self.classes = classes
        self.stride = stride
        self.model_layers_num = model_layers_num
        self.ckp = ckp
        self.init_k_len = init_k_len
        self.dense_len = dense_len

    def to_keras_model(self, **args):
        """
        将卷积神经网络转换成为Keras中能够支持的模型
        :param args: 参数列表
        :return: keras 中的神经网络模型
        """
        pass

    def __rshift__(self, other):
        other.stride = self.stride
        other.input_shape = self.input_shape
        other.classes = self.classes
        other.model_layers_num = self.model_layers_num
        other.ckp = self.ckp
        other.init_k_len = self.init_k_len
        other.dense_len = self.dense_len

    def __str__(self) -> str:
        """
        :return:当前类的结构信息
        """
        return f"zWell_model.convNet.convNetWork.ConvNet(\n" \
               f"\tstride={self.stride}, \n" \
               f"\tinput_shape{self.input_shape}, \n" \
               f"\tclasses={self.classes}\n" \
               f"\tmodel_layers_num={self.model_layers_num}, \n" \
               f"\tckp={self.ckp}, \n" \
               f"\tinit_k_len={self.init_k_len}, \n" \
               f"\tdense_len={self.dense_len}\n" \
               f")"
