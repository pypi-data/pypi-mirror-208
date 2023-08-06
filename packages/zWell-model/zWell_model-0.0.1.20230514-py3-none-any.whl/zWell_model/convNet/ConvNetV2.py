# -*- coding: utf-8 -*-
# @Time : 2023/5/14 10:27
# @Author : zhao
# @Email : liming7887@qq.com
# @File : ConvNetV2.py
# @Project : ZWell-model
from zWell_model.convNet.convNetWork import ConvNet


class ConvNetV2(ConvNet):

    def to_keras_model(self, **args):
        from keras import Sequential
        from keras.applications.densenet import layers
        init_filters = self.init_k_len
        model = Sequential(name=args.get('name', 'ConvNetV2'))
        # 卷积
        model.add(
            layers.Conv2D(init_filters, (3, 3), activation='relu', input_shape=self.input_shape)
        )
        # 卷积
        model.add(layers.Conv2D(init_filters, (3, 3), activation='relu'))
        # 标准化
        model.add(layers.BatchNormalization())
        # 池化
        model.add(layers.MaxPooling2D())
        # 随机失活
        model.add(layers.Dropout(0.25))
        for i in range(self.model_layers_num):
            if self.ckp == 2:
                init_filters <<= 1
            else:
                init_filters *= self.ckp
            # 卷积
            model.add(layers.Conv2D(init_filters, (3, 3), activation='relu'))
            # 卷积
            model.add(layers.Conv2D(init_filters, (3, 3), activation='relu'))
            # 标准化
            model.add(layers.BatchNormalization())
            # 池化
            model.add(layers.MaxPooling2D())
            # 随机失活
            model.add(layers.Dropout(0.25))
        # 计算出最后一层的卷积神经网络的核数
        num = init_filters << 1
        # 卷积
        model.add(layers.Conv2D(num, (3, 3), activation='relu'))
        # 卷积
        model.add(layers.Conv2D(num, (1, 1), activation='relu'))
        # 标准化
        model.add(layers.BatchNormalization())
        # 随机失活
        model.add(layers.Dropout(0.25))
        # 池化 同时降维
        model.add(layers.GlobalAveragePooling2D())

        # 开始全连接
        model.add(layers.Dense(self.dense_len))
        model.add(layers.BatchNormalization())
        model.add(layers.Dropout(0.5))
        # 输出类别
        model.add(layers.Dense(self.classes, activation='softmax'))
        return model
