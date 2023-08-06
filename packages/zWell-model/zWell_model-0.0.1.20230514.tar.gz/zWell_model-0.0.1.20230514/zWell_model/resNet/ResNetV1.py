# -*- coding: utf-8 -*-
# @Time : 2023/5/14 14:49
# @Author : zhao
# @Email : liming7887@qq.com
# @File : ResNetV1.py
# @Project : ZWell-model
from zWell_model.resNet import utils as ru
from zWell_model.resNet.resNetWork import ResNet


class ResNetV1(ResNet):
    def to_keras_model(self, **args):
        from keras import Input, Model
        from keras.layers import AveragePooling2D, Flatten, Dropout, Dense
        """定义残差网络"""
        inputs = Input(shape=self.input_shape)
        # 开始进行残差块之前进行一层卷积 然后开始进行残差块计算
        x = ru.res_module(inputs, k=self.init_k_len, stride=self.stride[0], chan_dim=self.chan_dim, red=self.red)
        # 准备进入其它残差块
        k_size = self.init_k_len
        if self.ckp == 2:
            k_size <<= 1
            for index in range(1, self.model_layers_num):
                x = ru.res_module(
                    x, k=k_size, stride=self.stride[index], chan_dim=self.chan_dim, red=self.red
                )
        else:
            k_size *= self.ckp
            for index in range(1, self.model_layers_num):
                x = ru.res_module(
                    x, k=k_size, stride=self.stride[index], chan_dim=self.chan_dim, red=self.red
                )
        # 均值池化
        x = AveragePooling2D()(x)
        # 扁平化
        x = Flatten()(x)
        # 失活
        x = Dropout(0.5)(x)
        # 全连接
        x = Dense(self.dense_len, activation='relu')(x)
        outputs = Dense(self.classes, activation='softmax')(x)
        model = Model(name=args.get('name', 'ResNetV1'), inputs=inputs, outputs=outputs)
        return model
