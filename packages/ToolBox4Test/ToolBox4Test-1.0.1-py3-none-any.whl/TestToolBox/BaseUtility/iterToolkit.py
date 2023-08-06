#!/usr/bin/python
# -*- coding: UTF-8 -*- 
"""   
@Author    : Gavin
@DateTime  : 2020/10/10 10:30
@Contact   : guowenwhy@foxmail.com

@Project   : TestToolBox
@File      : iterToolkit.py
@Describe  : json数据迭代遍历
————————————————————
@Version   : 2.1
"""
# update   : 10-10 - ver 0.1
# 1. 遍历/修改json
# 2. iterDict 遍历 key 值路径列表
# ————————————————————
# update   : 2021 - ver 1.0
# 1. myUpdate 迭代嵌套字典数据更新
# 1. myUpdatePro 迭代嵌套字典数据更新 链式路径"."查找
# ————————————————————
# update   : 2022/03/21 - ver 2.0
# 1. 合并组装字典测试参数
# 2.
# ————————————————————
# update   :
# 1.
# 2.
# ————————————————————
import inspect
import itertools

from jsonpath import jsonpath

import copy
from loguru import logger
import re


"""
生成器 - 自定义动态变量命名及赋值
"""


# 自动创建查找变量 - 筛选过滤接口响应数据 重新组装
def reformResp(key_list, response, path_pattern):
    result = {}
    for key in key_list:
        _temp_name = f"{key}_list"
        _temp_value = jsonpath(response, f"$..{path_pattern}.{key}")
        # 为自定义变量名赋值
        # exec(f"{_temp_name} = {_temp_value}")
        # result.append(eval(f"{key}_list"))
        result[_temp_name] = _temp_value
    return result


"""
python 模块、类对象、属性方法 抽象调用
"""


# 判断方法名是否中文字符 - 开发转发接口能力
def checkChinese(word):
    for alpha in word:
        if "\u4e00" <= alpha <= "\u9fff":
            return True
    return False


# 获取模块下所有类对象 -- CMS_Api_Lib.py
def getAllModuleMethod(package):
    # print(sys.modules.get("CMS_Api_Lib"))
    result = {}     # 名称列表即可，判断是否存在后，getattr调用
    for className, instanceObj in inspect.getmembers(package):
        if inspect.isclass(instanceObj) and checkChinese(className):
            # print(obj.__dict__.items())
            systemDict = {
                className: {
                    "classObj": instanceObj
                }
            }
            methodList = []
            for func in instanceObj.__dict__.keys():    # dir(obj):
                if inspect.ismethod(getattr(instanceObj, func)):
                    # print(func, getattr(obj, func))
                    methodList.append(func)
            systemDict.get(className).update({"methodList": methodList})
            result.update(systemDict)
    # print(result)
    return result


# 查找并调用 - getAllModuleMethod 已过滤方法
def reuseMethodList(clsName, funcName, systemDict):
    for cls, val in systemDict.items():
        if clsName == cls:
            if funcName in val.get("methodList"):
                return getattr(val.get("classObj"), funcName)
    return False


"""
迭代器 遍历生成测试数据 构造测试参数
"""

# paramDataPool = loadYaml(temptestDatePool("testData_ReqsParam.yml"))["testdataReqsParamPool"]


# 组装商家门店id v3.0 - 根据命令行参数 更新模板数据
def iterTarget2Keys(temp_datas, nest_dict):     # {a:[1], b: [2]} ->
    nestDict = temp_datas[nest_dict]

    keyName = nestDict["keyName"]
    keyValue = nestDict["keyValue"]
    tar = []
    for key in keyValue.keys():
        for val in keyValue[key]:
            com = {keyName[0]: key, keyName[1]: val}    # 只支持 2个key
            tar.append(com)
    # print(tar)
    return tar


# todo 测试数据更新方法 - 数据汇总
# 汇总笛卡尔积 - 合并关联key和普通key [{case1}, {case3}], [{case2}, {case4}] -> [{case1, case2}]
def iterPro(*testKwList):  # [{k1:v1, k2:v2},{k1:v1}], [{k3:v3, k4:v4},{k2:v2}]
    # print(testKwList[0])    # 输入列表变量
    resultList = []
    for item in itertools.product(*testKwList):
        # print(item)
        com = {}
        for i in item:
            com.update(i)
            resultList.append(com)
    print(resultList)
    return resultList  # -> [{}, {}]


# 1.0 只遍历 不找值
def iterDict(nestdata, dpath="", pathlist=None):
    """
    迭代配置结构
    :param nestdata: 嵌套字典
    :param dpath: 路径中转值
    :param pathlist: 路径例表
    :return:
    """

    if pathlist is None:
        pathlist = []
    if isinstance(nestdata, dict):  # 使用isinstance检测数据类型
        for k in nestdata.keys():  # 遍历一层字典键
            # _path = copy.deepcopy(dpath)     # 深复制
            # logger.debug(_path)
            _path = f"{dpath}.{k}"
            pathlist.append(_path)
            # logger.debug(dpath)
            iterDict(nestdata[k], _path, pathlist)

    elif isinstance(nestdata, list):    # 嵌套列表
        for i in nestdata:
            # 嵌套列表
            if isinstance(i, dict):
                _path = nestdata.index(i)   # list index
                # logger.debug(_path)
                _path = f"{dpath}.{_path}"  # iter path
                pathlist.append(_path)
                # logger.debug(dpath)
                iterDict(i, _path, pathlist)
            else:
                break

    # else:
        # dpath = f"{dpath}.{nestdata}"
        # logger.debug(dpath)
        # pathlist.append(dpath)

    return pathlist


# 1.0 只遍历 不找值 - 组成list -> [[a,d],[],[]]
# 遍历字典， 返回路径列表
def iterDict2List(dictData, dpath=None, pathList=None):
    # print(dictData)
    if dpath is None:
        dpath = []
    if pathList is None:
        pathList = []
    if isinstance(dictData, dict):  # 使用isinstance检测数据类型
        for k in dictData.keys():  # 遍历一层字典键
            _path = copy.deepcopy(dpath)  #
            _path.append(k)
            iterDict2List(dictData[k], _path, pathList)

    elif isinstance(dictData, list):    # 列表数据
        for data in dictData:
            _path = copy.deepcopy(dpath)
            # print(data)
            _path.append(data)
            pathList.append(_path)

    else:
        _path = copy.deepcopy(dpath)
        _path.append(dictData)
        pathList.append(_path)

    return pathList  # , npath


# test
# dp = iterDict(paramDataPool)
# print(dp)


# 2.0 遍历找值
# 问题!!!!!!!
# 关键词更新方式? key索引 - 定位&数据 - 自动更新
# 问题? 嵌套列表 如何遍历?
def findIterDict(jsondata, target, dpath="", pathlist=None):
    """
    迭代配置结构
    :param jsondata: 嵌套字典
    :param target:
    :param dpath: 路径中转值
    :param pathlist: 路径例表
    :return:
    """

    if pathlist is None:
        pathlist = []

    if isinstance(jsondata, dict):  # 使用isinstance检测数据类型
        for k, v in jsondata.items():  # 遍历一层字典键
            _path = copy.deepcopy(dpath)     # 深复制
            # logger.debug(_path)
            _path = f"{_path}.{k}"
            # logger.debug(dpath)

            if target == k:
                pathlist.append(_path)
            else:
                findIterDict(v, target, _path, pathlist)

    # 只遍历嵌套列表 不需要底层数值？
    elif isinstance(jsondata, list):
        for i in jsondata:
            _path = copy.deepcopy(dpath)  # 深复制
            # _path = jsondata.index(i)  # list index
            # logger.debug(_path)
            _path = f"{_path}.{jsondata.index(i)}"  # iter path
            # logger.debug(dpath)
            findIterDict(i, target, _path, pathlist)

    return pathlist


# 更新json值
# def editJson(jsondata, keypath, value):
def editJson(jsondata, keydicts):
    #     jsondict = json.load(jsondata)
    jsondict = jsondata

    # copy模板
    # jsondict = param_temp[jsondata].copy()

    for keypath, value in keydicts.items():

        key_ = keypath.split(".")
        # 去掉第一个”.“前空值
        key_.pop(0)

        key_len = len(key_)
        temp = jsondict
        i = 0
        while i < key_len:
            #         print(i, key_len)
            if i + 1 == key_len:
                # key_[i] = "0"
                try:
                    temp[key_[i]] = value
                    i += 1
                except:  # index of list
                    temp[eval(key_[i])] = value
                    i += 1
            else:
                try:
                    temp = temp[key_[i]]
                    i += 1
                except:  # index of list
                    temp = temp[eval(key_[i])]
                    i += 1
        #     print(jsondict)
    return jsondict


# 更新嵌套json串
def myUpdate(nestData, new):
    if isinstance(nestData, dict):
        for nestkey, nestval in nestData.items():  # 遍历一层字典键
            for _k, _v in new.items():
                # logger.debug(f"更新对象键值对: {_k}: {_v}\n匹配键值: {nestkey}: {nestval}")
                if nestkey == _k:
                    # logger.debug(f"判断数据类型: {type(nestval)} == {type(_v)}")
                    if type(nestval) == type(_v):   # val 数据类型相同
                        nestData.update({_k: _v})
                    # elif isinstance(nestval, list) and isinstance(_v, str):
                    elif isinstance(nestval, list):
                        nestval.append(_v)
                    elif isinstance(nestval, int) and isinstance(_v, str):
                        nestData.update({_k: int(_v)})

                    # key = None / null 等例外
                    else:
                        nestData.update({_k: _v})

                else:
                    myUpdate(nestval, new)

    # 只遍历嵌套列表 不需要底层数值？
    elif isinstance(nestData, list):
        for nest_i in nestData:
            myUpdate(nest_i, new)

    return nestData


# 更新嵌套json串 v2.0 - data.key 嵌套关系 & 最大更新次数
def myUpdatePro(nestData, new):
    # logger.debug(nestData, new)
    if isinstance(nestData, dict):
        for nestkey, nestval in nestData.items():  # 遍历一层字典键
            for _k, _v in new.items():
                # logger.debug(f"更新对象键值对: {_k}: {_v}")
                # logger.debug(f"匹配键值: {nestkey}: {nestval}")
                _k_path = _k.split(".")
                if len(_k_path) > 1:     # 嵌套键值对  {data.key.zzz: val}
                    for _index in range(len(_k_path)-1):   # [data, key] 多层嵌套 定位地址
                        _remain = _k_path[_index]
                        if nestkey == _remain:  # data // key // 无(zzz)
                            _replace = _k.replace(f"{_remain}.", "", 1)
                            # logger.debug(f"nestval, _remain: \n{nestval}, {_replace}")
                            myUpdatePro(nestval, {_replace: _v})
                        # 遍历列表值无匹配 !!! 列表内字符串
                        elif isinstance(nestval, dict) or isinstance(nestval, list):
                            myUpdatePro(nestval, new)

                else:   # 普通键值对 {k: v}
                    if nestkey == _k:
                        # logger.debug(f"判断数据类型: {type(nestval)} == {type(_v)}")
                        if type(nestval) == type(_v):   # val 数据类型相同
                            nestData.update({_k: _v})
                        # elif isinstance(nestval, list) and isinstance(_v, str):
                        elif isinstance(nestval, list):
                            nestval.append(_v)
                        elif isinstance(nestval, int) and isinstance(_v, str):
                            nestData.update({_k: int(_v)})
                            # times -= 1
                            # if times == 0:
                            #     raise Getoutofloop()

                        # key = None / null 等例外
                        else:
                            nestData.update({_k: _v})

                    # 遍历列表值无匹配 !!! 列表内字符串
                    elif isinstance(nestval, dict) or isinstance(nestval, list):
                        myUpdatePro(nestval, new)

    # 只遍历嵌套列表 不需要底层数值？
    elif isinstance(nestData, list):
        for nest_i in nestData:
            if isinstance(nest_i, dict) or isinstance(nest_i, list):
                myUpdatePro(nest_i, new)

    else:
        logger.error(f"待更新数据类型错误!\n{nestData, new}")

    return nestData


# 判断 data.key 嵌套 键 数据
def evalDoc(nestData):
    if isinstance(nestData, dict):
        for nestkey, nestval in nestData.items():  # 遍历一层字典键
            # logger.debug(f"{nestkey}: {nestval}")
            if isinstance(nestval, str) and (nestval[:2] == 'f"' or nestval[:2] == "f'"):
                # do 自动更新时间戳 或内嵌函数等
                # logger.debug(f"{nestkey}: {eval(nestval)}")
                nestData.update({nestkey: eval(nestval)})
            else:
                evalDoc(nestval)

    # 只遍历嵌套列表 不需要底层数值？
    elif isinstance(nestData, list):
        for nest_i in nestData:
            if isinstance(nest_i, dict) or isinstance(nest_i, list):
                evalDoc(nest_i)
            elif isinstance(nest_i, str) and (nest_i[:2] == 'f"' or nest_i[:2] == "f'"):
                logger.debug(f"eval - {nestData}: {eval(nest_i)}")
                # nestData.pop(nestData.index(nest_i))
                nestData.remove(nest_i)
                nestData.append(eval(nest_i))

    return nestData


# header 请求头 cookie更新
def replaceHead(cookies, new_obj):  # -> {k:v, k:v}
    for re_key, re_val in new_obj.items():
        # logger.debug(f"{re_key}, {re_val}")
        pat_ = re.compile(f"{re_key}=.*?;")     # 替换正则规则
        cookies = pat_.sub(f"{re_key}={re_val};", cookies)   # 替换
    # logger.debug(cookies)
    return {"Cookie": cookies}


# 更新cookie
def newCookie(new_obj):
    for re_key, re_val in new_obj.items():
        new_cookies = f"{re_key}={re_val}"
        # print({"Cookie": new_cookies})
        return {"Cookie": new_cookies}


if __name__ == '__main__':

    k1 = {"A": 1111, "B": [{"B1": "bb"}, "b"], "C": {"C3": 33, "CC2": [123, "C3", {"C123": "ccc"}]}, "DD": ["D", {"D4": 44, "DD": ""}, {"DD": ""}]}
    # k2 = {"CC2.C123": "999"}
    # k2 = {"B1": "999"}
    k2 = {"DD.DD": "999"}

    tt = "data.key.zzz.abc"
    # t1 = tt.split(".")

    # print("tt".split("."))
    # print(range(len(t1)))

    # for i in range(len(t1)-1):
    #     print(i)
    #     print(t1[i])
    #     print(t1[i+1:])
    #
    #     # _re = ""
    #     # for j in t1[i+1:]:
    #     #     _re += f".{j}"
    #     # print(_re)
    #
    #     tst = tt.strip(f"{t1[i]}.")
    #     print(tst)

    # myUpdatePro(k1, k2)
    # print(myUpdatePro(k1, k2))
    # print(myUpdatePro(k1, k2))


