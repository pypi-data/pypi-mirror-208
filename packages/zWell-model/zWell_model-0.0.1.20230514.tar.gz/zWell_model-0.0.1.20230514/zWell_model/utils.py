# -*- coding: utf-8 -*-
# @Time : 2023/5/13 21:32
# @Author : zhao
# @Email : liming7887@qq.com
# @File : utils.py
# @Project : Z-model

def if_none(check_data, def_data):
    """
    检查对象是否为空 如果为空就返回 def_data
    :param check_data: 被检查的对象
    :param def_data: 当检查不通过返回的对象
    :return: if check_data is None return def_data else return check_data
    """
    if check_data is None:
        return def_data
    else:
        return check_data


def check_list_len(list_data, correct_length, param_name):
    """
    检查list对象的类型与长度。
    :param list_data: 需要被检查的对象。
    :param correct_length: 期望的list的长度。
    :param param_name: 被判断的对象的描述信息，通常是该参数的名字或其它信息。
    :return: 如果被判断的对象合法 将会返回None 反之直接抛出异常信息。
    """
    t = type(list_data)
    if t == list:
        length = len(list_data)
        if length != correct_length:
            raise_len_error(param_name, length, correct_length)
    else:
        raise_type_error(param_name, t, list)


def raise_type_error(wrong_parameter, error_type, correct_type):
    """
    抛出类型错误的异常
    :param wrong_parameter:对于错误参数数值的描述。
    :param error_type: 错误的数据类型
    :param correct_type: 正确的数据类型
    """
    raise TypeError(f"期望的类型为：{correct_type}，但是您提供的类型为：{error_type}\n"
                    f"\tThe expected type is: {correct_type}, but the type you provided is: {error_type}\n"
                    f"\tWrong parameter => {wrong_parameter}")


def raise_len_error(wrong_parameter, error_len, correct_len):
    """
    抛出元素数量错误的异常
    :param wrong_parameter:对于错误参数数值的描述。
    :param error_len: 错误的数据长度
    :param correct_len: 正确的数据长度
    """
    raise IndexError(f"期望的长度为：{correct_len},但是您提供的容器元素数量为：{error_len}\n"
                     f"\tThe expected length is: {correct_len}, "
                     f"but the number of container elements you provided is: {error_len}\n"
                     f"\tWrong parameter => {wrong_parameter}")
