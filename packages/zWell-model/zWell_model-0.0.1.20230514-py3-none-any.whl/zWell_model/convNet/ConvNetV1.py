# -*- coding: utf-8 -*-
# @Time : 2023/5/14 10:24
# @Author : zhao
# @Email : liming7887@qq.com
# @File : ConvNetV1.py
# @Project : ZWell-model
from zWell_model.convNet.convNetWork import ConvNet


class ConvNetV1(ConvNet):
    """
    第一种基本的卷积神经网络模型
    """

    def to_keras_model(self, **args):
        from keras import Sequential
        from keras.layers import Convolution2D, Activation, MaxPooling2D, Flatten, Dense
        init_filters = self.init_k_len
        model = Sequential(name=args.get('name', 'ConvNetV1'))
        # 添加第一层神经元 这里第一层是卷积
        model.add(
            Convolution2D(
                # 指定 初始 个滤波器（卷积核）
                filters=init_filters,
                # 指定卷积核大小
                kernel_size=2,
                # 指定生成规则 设成same会自动加padding，保证输出是同样的大小。
                padding='same',
                # 设置卷积层第一次的输入数据维度
                batch_input_shape=self.input_shape,
            )
        )
        # 添加一层激活函数
        model.add(Activation('relu'))
        # 添加一层池化层
        model.add(
            MaxPooling2D(
                # 指定池化层核的尺寸 这里是 2x2
                pool_size=2,
                # 指定步长 2x2
                strides=2,
                # 指定池化层生成规则
                padding='same'
            )
        )

        # 添加所有剩余层的卷积层
        if self.ckp == 2:
            for i in range(self.model_layers_num):
                # 添加一层卷积
                init_filters <<= 1
                model.add(Convolution2D(filters=init_filters, kernel_size=2, padding='same', strides=self.stride[i]))
                # 添加一层激活函数
                model.add(Activation("relu"))
                # 添加一层池化
                model.add(MaxPooling2D(pool_size=2, padding='same'))
        else:
            for i in range(self.model_layers_num):
                # 添加一层卷积
                init_filters *= self.ckp
                model.add(Convolution2D(filters=init_filters, kernel_size=2, padding='same', strides=self.stride[i]))
                # 添加一层激活函数
                model.add(Activation("relu"))
                # 添加一层池化
                model.add(MaxPooling2D(pool_size=2, padding='same'))

        # 将矩阵扁平化准备全连接
        model.add(Flatten())
        # 正式进入全连接神经网络，添加全连接神经元(具有1024个神经元的层)
        model.add(Dense(self.dense_len))
        # 添加激活函数
        model.add(Activation("relu"))
        # 再一次添加一层 8 个神经元的网络层(每个神经元代表一个类别)
        model.add(Dense(self.classes))
        # 添加激活函数 softmax 用于计算概率得分
        model.add(Activation("softmax"))
        return model
