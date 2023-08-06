# -*- coding: utf-8 -*-
# @Time : 2023/5/13 20:21
# @Author : zhao
# @Email : liming7887@qq.com
# @File : resNetWork.py
# @Project : Keras-model
import copy

import zWell_model.utils as zu
from zWell_model.allModel import AllModel


class ResNet(AllModel):
    """
    残差神经网络最基础的架构对象。
    """

    def __init__(self, k, stride, input_shape, classes,
                 chan_dim=-1, red=True,
                 reg=0.0001, bn_eps=2e-5,
                 bn_mom=0.9, model_layers_num=4,
                 ckp=2, init_k_len=64, dense_len=512
                 ):
        """
        构造出来一个残差神经网络对象
        :param k: 每一个残差块中的输出通道数量，需要注意的是，这是一个list 作为每一个残差块的输出描述。
        :param stride: 每一个残差块的卷积步长 需要注意的是，这是一个list，作为每一个残差块的卷积步长。
        :param chan_dim: 每一个残差块在进行批量归一化操作时依赖的轴 需要注意的是，这是一个list，作为每一个残差块的归一化轴编号。
        :param input_shape: 残差神经网络的输入维度元组
        :param classes: 残差神经网络的分类方式
        :param red: 是否使用单通道方式进行处理
        :param reg: 残差块中的L2正则化系数
        :param bn_eps: 用于避免批量归一化除以0
        :param bn_mom: 定义批量归一化操作时的动态均值的动量
        :param model_layers_num: 残差神经网络层数量
        :param ckp: 卷积层之间的卷积核数量等比数值
        :param init_k_len 第一层残差块中的卷积核数量
        :param dense_len 残差结束之后，全连接神经元第一层的神经元数量
        """
        super().__init__()
        # 检查 k 并赋值k
        zu.check_list_len(k, model_layers_num, "Number of output channels in each residual block:[k]")
        self.k = k

        # 检查步长 并 赋值步长
        zu.check_list_len(stride, model_layers_num, "Convolutional step size for each residual block:[stride]")
        self.stride = stride

        self.input_shape = input_shape
        self.classes = classes
        self.chan_dim = chan_dim
        self.red = red
        self.reg = reg
        self.bn_eps = bn_eps
        self.bn_mom = bn_mom
        self.model_layers_num = model_layers_num
        self.ckp = ckp
        self.init_k_len = init_k_len
        self.dense_len = dense_len

    def to_keras_model(self, **args):
        """
        将当前神经网络模型对象转换成为 keras 中的模型对象
        :param args: 需要使用到的参数
        :return: 转换之后的 keras 模型对象
        """
        pass

    def __rshift__(self, other):
        """
        使用拷贝的方式将当亲残差网络模型中的所有属性拷贝到另一个残差网络模型对象中，常用于不同配置的网络之间的属性覆写操作。
        能够在不重新创建新神经网络对象的前提下复制神经网络对象
        :param other: 拷贝之后的新神经网络模型。
        :return: 拷贝之后的新神经网络模型。
        """
        other.k = copy.copy(self.k)
        other.stride = copy.copy(self.stride)
        other.input_shape = self.input_shape
        other.classes = self.classes
        other.chan_dim = self.chan_dim
        other.red = self.red
        other.reg = self.reg
        other.bn_eps = self.bn_eps
        other.bn_mom = self.bn_mom
        other.model_layers_num = other.model_layers_num
        other.ckp = self.ckp
        other.init_k_len = self.init_k_len
        other.dense_len = self.dense_len

    def __str__(self) -> str:
        return "zWell_model.resNet.resNetWork.ResNet(\n" \
               f"\tk={self.k}\n" \
               f"\tstride={self.stride}\n" \
               f"\tinput_shape={self.input_shape}\n" \
               f"\tclasses={self.classes}\n" \
               f"\tchan_dim={self.chan_dim}\n" \
               f"\tred={self.red}\n" \
               f"\treg={self.reg}\n" \
               f"\tbn_eps={self.bn_eps}\n" \
               f"\tbn_mom={self.bn_mom}\n" \
               f"\tmodel_layers_num={self.model_layers_num}\n" \
               f"\tckp={self.ckp}\n" \
               f"\tinit_k_len={self.init_k_len}\n" \
               f"\tdense_len={self.dense_len}\n" \
               ")"
