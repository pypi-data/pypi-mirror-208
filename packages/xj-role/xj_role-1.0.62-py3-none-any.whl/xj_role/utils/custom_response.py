# encoding: utf-8
"""
@project: djangoModel->tool
@author: 孙楷炎
@Email: sky4834@163.com
@synopsis: 返回协议封装工具
@created_time: 2022/6/15 14:14
"""
import json

from django.http import JsonResponse


# json 结果集返回
def parse_json(result):
    if not result is None:
        if type(result) is str:
            try:
                result = json.loads(result.replace("'", '"').replace('\\r', "").replace('\\n', "").replace('\\t', "").replace('\\t', ""))
            except Exception as e:
                return result
        if type(result) is list or type(result) is tuple:
            for index, value in enumerate(result):
                result[index] = parse_json(value)
        if type(result) is dict:
            for k, v in result.items():
                result[k] = parse_json(v)
    return result


# 数据返回规则
def util_response(data='', err=0, msg='ok', is_need_parse_json=True):
    """
    http 返回协议封装
    :param data: 返回的数据体
    :param err: 错误码，一般以1000开始，逐一增加。登录错误为6000-6999。
    :param msg: 错误信息，一般为服务返回协议中的err,自动解析内容
    :return: response对象
    """
    data = parse_json(data) if is_need_parse_json else data
    response_json = {'err': err, 'data': data}
    # 解析msg字符串
    try:
        msg_list = msg.split(";")
        if len(msg_list) <= 1:
            response_json["msg"] = msg
        else:
            for i in msg_list:
                [key, value] = i.split(":")
                response_json[key] = value
    except Exception as e:
        print("返回异常，请返回异常前替换处理分号和冒号，避免返回协议冲突")
        response_json["msg"] = msg

    return JsonResponse(response_json)
