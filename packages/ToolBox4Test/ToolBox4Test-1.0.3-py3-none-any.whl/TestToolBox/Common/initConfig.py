#!/usr/bin/python
# -*- coding: UTF-8 -*- 
"""   
@Author    : Gavin
@DateTime  : 2022/1/8 22:58
@Contact   : guowenwhy@foxmail.com

@Project   : TestToolBox
@File      : initConfig
@Describe  : 初始化配置参数
————————————————————
@Version   : 1.0
"""
# update   : 2022/1/8
# 1. 接口文档转换为字典对象
# 2. 
# ————————————————————
# update   : 03/18 - ver.1.0
# 1. 公共配置类 - 父类
# 2. 
# ————————————————————
# update   : 04/01
# 1. 数据工厂 `DataFactory` 父类，构建底层数据处理方法
# 2.
# ————————————————————
# update   :
# 1.
# 2.
# ————————————————————
import csv
import itertools

from TestToolBox import Project_Dir
from loguru import logger
from faker import Faker

from TestToolBox.BaseUtility.toolkit import loadYaml, lazy, DictObjection, mkdir


"""
Pytest 公共配置
"""


def init_Api_ids(fixture_value):  # ids 参数化
    # id = f"{item.name}"
    id = f""
    # 判断类型
    if isinstance(fixture_value, dict):
        # 详情参数
        for key, val in fixture_value.items():
            if isinstance(val, str):
                id = f"{id}#{key}:{val[:7]}-"
            else:
                id = f"{id}#{key}:{val}-"
        # 精简参数 - 仅title标识
        # for key, val in fixture_value.items():
        #     if key == "title":
        #         id = f"{id}#{key}:{val}-"
        #     else:
        #         pass
        return id

    if isinstance(fixture_value, list):
        for val in fixture_value:
            id = f"{id}.{val}-"
        return id


def init_UI_ids(fixture_value):  # ids 参数化
    # id = f"{item.name}"
    id = f""
    # 判断类型
    if isinstance(fixture_value, dict):
        # 详情参数
        # for key, val in fixture_value.items():
        #     if isinstance(val, str):
        #         id = f"{id}#{key}:{val[:7]}-"
        #     else:
        #         id = f"{id}#{key}:{val}-"
        # 精简参数 - 仅title标识
        for key, val in fixture_value.items():
            if key == "title":
                id = f"{id}#{key}:{val}-"
            else:
                pass

        return id

    if isinstance(fixture_value, list):
        for val in fixture_value:
            id = f"{id}.{val}-"
        return id


"""
加载 测试数据 组装成测试数据
todo 如何解决 列表[] 字典{} 格式读取后转为 str 格式？
"""


# 数据工厂
class DataFactory:
    pass


"""
# 03/23 笛卡尔积 - 遍历加载枚举值 生成接口测试数据
def iterEnum(api_enums):
    result = []
    for item in itertools.product(*list(api_enums.values())):
        result.append(item)
    return result


def iterEnum2csv(csv_file, api_enums):
    result = iterEnum(api_enums)
    CSVFactory(csv_file).recorder(result, title=list(api_enums.keys()), delimiter=";")


# 2022/03/21 合并组装字典测试参数
def combineKeysValue(key_list, *value_list, same_data_list=False, default=None):
    resultList = []
    if same_data_list:
        valuePool = itertools.zip_longest(*value_list, fillvalue=default)
    else:
        valuePool = value_list
    for val in valuePool:
        _temp = dict(itertools.zip_longest(key_list, val, fillvalue=default))
        resultList.append(_temp)
    # print(resultList)
    return resultList
"""


# csv 测试数据工厂
class CSVFactory:

    def __init__(self, csv_file):
        self.csvPath = csv_file

    # 1 - 03/21 合并组装字典测试参数
    @staticmethod
    def combineKeysValue(key_list, *value_list, keyName=None, sameValue=False, default=None):
        resultList = []
        resultDict = {}
        if sameValue:
            # sameValue 用于同等长度数据，例如查询数据列表，jsonpath 获取批量数据
            valuePool = itertools.zip_longest(*value_list, fillvalue=default)
        else:
            valuePool = value_list
        for val in valuePool:
            _temp = dict(itertools.zip_longest(key_list, val, fillvalue=default))
            # 使用key命名字典 可视化数据
            if keyName:
                resultDict[_temp.get(keyName)] = _temp
            resultList.append(_temp)
        if not keyName:
            # logger.debug(resultList)
            return resultList
        else:
            return resultDict

    @staticmethod
    def iterEnum(api_enums):
        result = []
        for item in itertools.product(*list(api_enums.values())):
            result.append(item)
        return result

    # 2 - 03/23 笛卡尔积 - 遍历加载枚举值 生成接口测试数据
    def iterEnum2csv(self, api_enums):
        result = self.iterEnum(api_enums)
        self.recorder(result, title=list(api_enums.keys()), delimiter=";")

    # 3 - 读取 csv 测试数据 转换为测试参数 request.param
    def trans2Params(self, **kwargs):
        csvData = self.reader(delimiter=";")     # csv 读取数据格式默认为str 'period': '[]'
        # do 转换csv中储存的 列表[] 字典{} 格式
        param_key = csvData[0]
        param_val = csvData[1:]
        return self.combineKeysValue(param_key, *param_val, **kwargs)

    def recorder(self, msg, title=None, _type="w", delimiter=","):
        mkdir(self.csvPath)
        with open(self.csvPath, _type, newline='', encoding="utf-8") as cfile:
            pen = csv.writer(cfile, delimiter=delimiter)
            # 读取文件判断有无内容行
            with open(self.csvPath, 'r', newline='') as rf:
                # reader = csv.reader(rf)
                # if not [row for row in reader]:     # 写入标题
                if title:     # 写入标题
                    pen.writerow(title)
                    pen.writerows(msg)
                else:
                    # for d in data:
                    pen.writerows(msg)
        return True

    def reader(self, delimiter=","):
        result = []
        with open(self.csvPath) as cf:
            lines = cf.readlines()
            for i, line in enumerate(lines):
                data_list = line.strip().split(delimiter)
                # print(data_li)
                _temp = []
                for data in data_list:
                    if "[" in data or "{" in data:
                        _temp.append(eval(data))
                    else:
                        _temp.append(data)
                result.append(_temp)
        return result


"""
配置化实例类 01/08
"""


# 公共配置类 - 父类
class CommonConfig:
    # 类.属性 - 接口文档/页面元素配置文档
    # sourceFile = demoFile
    # sourceYamlData = loadYaml(sourceFile)
    
    def __init__(self, file_path):
        # super().__init__(file_path)
        # super().__init__()
        self._sourceData = loadYaml(file_path)
        # self._a = 1   # 类实例返回对象为 init 下键值对
    
    @lazy  # 属性方法
    def source(self):
        return self._sourceData
        # return dictObject(self._sourceData)
    
    # 等价 getFileData 的 类属性调用
    @lazy
    def classData(self):
        return DictObjection.transferDict(self._sourceData)
        # 期望返回对象能够使用 finder 方法
    
    # 子类的实例继承了父类的class_method类方法，调用该方法，调用的是子类的方法和子类的类属性 - .getFileData()
    # @classmethod
    # def getFileData(cls):
    #     return dictObject(cls.source)
    
    # @staticmethod
    # def finder(self, path_list, root_data=None):
    #     if root_data:
    #         root = root_data
    #     else:
    #         root = dictObject(self.__source)
    #     for path in path_list:
    #         # print("root", root)
    #         # print("path_list", path_list)
    #         root = getattr(root, path)
    #     return root


"""
1、如果子类 继承父类不做初始化(这里指的是子类中没有__init__初始化函数)，那么这时子类会自动继承父类 属性。 
2、如果子类 继承父类 做了初始化(这里指的是子类中有__init__函数，对子类特有的属性进行了初始化)，且不调用super初始化父类构造函数，那么子类 不会自动继承父类的属性
3、如果子类 继承父类 做了初始化，且调用了super初始化了父类的构造函数，那么子类也会继承父类的属性。
注意：python3，super(子类名，self).__init__(父类属性)， 其中在子类初始化函数中要将父类的__init__函数中的父类属性全部包含进来
"""


# 模块配置 - 子类


# class childConfig(CommonConfig):
#     pass
#
#     def __init__(self):
#         self.a = "a"
#         super().__init__(self)


"""
类属性生成器 generation
"""


# demo
def __generator(args):
    logger.debug(f"Gen start ...")
    count = 0
    object_attr = GenDemo.api_object
    # for i in range(2):
    for key in object_attr.keys():
    
        # setattr(GenDemo, f"funcName{count}", GenDemo.getFunc(a, b, c=True))
        setattr(GenDemo, f"{object_attr.get(key).get('DESC')}", args(object_attr, key))

        count += 1

    logger.debug(f"Gen complete!")


class GenDemo:
    api_doc = f"{Project_Dir}/Common/Api_Template_Doc.yml"
    api_object = CommonConfig(api_doc).classData

    @staticmethod
    def getFunc(*args, **kwargs):
        def func(self):  # self 是类实例化对象
            # self.apiReqs(*args, **kwargs)
            return self.apiReqs(*args, **kwargs)
            # return CMSBasicConfig(*args, **kwargs)

        return func

    # @classmethod
    # 类属性承载接对象 / 接口实例
    def apiReqs(self, *args, **kwargs):
        logger.debug(f"{self.api_object}")
        logger.info(f"{args}, {kwargs}")
        return args, kwargs


if __name__ == '__main__':
    pass

    """
    类属性生成器 generation
    """

    # __generator(GenDemo.getFunc)  # GenApiReqs 类绑定接口方法
    # logger.debug(dir(GenDemo()))
    #
    # demo = GenDemo()

    """
    # 实例化 调试
    """
    
    # 期望返回对象能够使用 finder 方法
    # 1.dict字典
    # file_data = loadYaml(test_api)
    #
    # dict1 = dictObject(file_data)
    #
    # # from BaseUtility.toolkit import DictionObject
    # # dict1 = DictionObject().transferDict(file_data)
    #
    # print(dict1)
    # print(dict1.finder(["loginCMS", "REQUEST", "HOST"]))
    
    # 2.加载文件 封装类
    # dict1 = CommonConfig(test_api)  # 类实例返回对象为 init 下键值对
    # print(type(dict1))  # 转换后实例对象 <class 'Common.initConfig.CommonConfig'>
    # print(dict1)  # 转换后实例对象
    
    # print(dict1.test())
    # print(type(dict1.source))  # 转换后实例对象._sourceData
    # source() TypeError: 'Objectionary' object is not callable
    # <class 'BaseUtility.toolkit.Objectionary'>
    
    # print(dict1.source)  # 转换后实例对象._sourceData
    # <bound method CommonConfig.source of <Common.initConfig.CommonConfig object at 0x7fe2a81710d0>>
    
    # print(dict1.source)
    # print(dict1.classData.loginCMS)
    
    # obj2 = dict1.classData
    
    # 转换后对象 finder方法
    # print(obj2.finder(["loginCMS", "REQUEST", "HOST"], obj2))
    # print(obj2.finder(["loginCMS", "REQUEST", "HOST"]))
    # print(obj2.loginCMS.finder(["REQUEST", "HOST"]))

    # 包含列表类型数据场景
    # list1 = obj2.loginCMS.REQUEST.QUERY
    # print(type(list1))  # <class 'list'>
    # print(type(list1[0].a))   # AttributeError: 'dict' object has no attribute 'a'
    # print(type(list1[0].get("a")))
    # 类型转换后 无法兼容列表方法
    # print(list1[0])   # 无法兼容列表方法 KeyError: 0
    # print(list1.index0)
    # print(list1.index0.a)
