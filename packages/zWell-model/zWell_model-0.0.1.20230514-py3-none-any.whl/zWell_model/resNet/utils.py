# -*- coding:utf-8 -*-

def res_module(
        data, k, stride, chan_dim,
        red=False, reg=0.0001, bn_eps=2e-5, bn_mom=0.9
):
    """
    生成一个残差块
    :param data:上一层数据的输入
    :param k: 残差快的数据输出通道数
    :param stride: 卷积步长
    :param chan_dim: 批量归一化层中，使用的归一化轴。
    :param red: 是否对恒等映射进行 1x1 卷积，调整通道数量
    :param reg: 定义正则化超参数
    :param bn_eps: 用于避免批量归一化除以0
    :param bn_mom: 定义批量归一化操作时的动态均值的动量
    :return: 残差块的输出
    """
    from keras.layers import BatchNormalization, add, AveragePooling2D
    from keras.layers.convolutional import Conv2D
    from keras.layers.core import Activation
    from keras.regularizers import l2
    # 将残差计算需要的恒等数值获取到，这里是将输入数据作为恒等数值
    shortcut = data
    # 残差块中的第一层卷积 1x1 包含 归一化 激活 卷积
    bn1 = BatchNormalization(axis=chan_dim, epsilon=bn_eps, momentum=bn_mom)(data)
    act1 = Activation('relu')(bn1)
    conv1 = Conv2D(
        filters=int(k * 0.25), kernel_size=(1, 1),
        # 不适用bias参数  指定L2 正则
        use_bias=False, kernel_regularizer=l2(reg)
    )(act1)
    # 残差块中的第二层卷积 3x3 包含 归一化 激活 卷积
    bn2 = BatchNormalization(axis=chan_dim, epsilon=bn_eps, momentum=bn_mom)(conv1)
    act2 = Activation('relu')(bn2)
    conv2 = Conv2D(
        filters=int(k * 0.25), kernel_size=(3, 3),
        strides=stride, padding='same', use_bias=False, kernel_regularizer=l2(reg)
    )(act2)
    # 残差块中的第三层卷积 1x1 包含归一化 激活 卷积
    bn3 = BatchNormalization(axis=chan_dim, epsilon=bn_eps, momentum=bn_mom)(conv2)
    act3 = Activation('relu')(bn3)
    conv3 = Conv2D(
        filters=k, kernel_size=(1, 1),
        strides=stride, padding='same', use_bias=False, kernel_regularizer=l2(reg)
    )(act3)
    # 判断是否需要进行参数减小，如果需要就再进行 1x1 卷积 并将卷积结果作为恒等参数 使用这个新恒等计算
    if red:
        shortcut = Conv2D(k, kernel_size=(1, 1), strides=stride, use_bias=False, kernel_regularizer=l2(reg))(act1)
    # 判断恒等参数是否需要尺寸调整，如果需要就将恒等数值进行池化 使得恒等参数的维度与卷积结果相同
    if stride != 1:
        shortcut = AveragePooling2D(pool_size=stride)(shortcut)
    # 计算出残差 并将残差返回出去 残差 = 恒等映射 + 卷积输出
    return Activation('relu')(add([shortcut, conv3]))
