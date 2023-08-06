#!/usr/bin/python
# -*- coding: UTF-8 -*- 
"""   
@Author    : Gavin
@DateTime  : 2020/8/29 17:28
@Contact   : guowenwhy@foxmail.com

@Project   : TestToolBox
@File      : toolkit.py
@Describe  : 工具箱 文本 数据处理
————————————————————
@Version   : 0.1 
"""
# update   : 08-29
# 1. 封装记录埋点数据方法,便于扩展
# 2. 充分利用请求&响应数据代理工具,挖掘数据价值
# ————————————————————
# update   : 
# 1.
# ————————————————————


import imp
import traceback
from functools import wraps

import os
import time

import subprocess
import sys
import re

from loguru import logger

from jsonpath import jsonpath
import yaml
import json
import csv
# import xlrd
# import xlwt
# import xldate_as_tuple, xlscopy

from pycallgraph import PyCallGraph
from pycallgraph import Config
from pycallgraph import GlobbingFilter
from pycallgraph.output import GraphvizOutput

"""
# 索引数据表格
"""


# 将变量名转换成字符串实例
def get_varsname(obj, namespace=None):
    if namespace is None:
        namespace = globals()
    print(namespace)
    # return [name for name in namespace if namespace[name] is obj]   # ['a']
    return [name for name in namespace if namespace[name] is obj][0]  # a


# print(namestr(a, globals()), '\n', namestr(a, globals())[0])

# print((lambda args: [name for name in locals() if globals()[name] is args][0])(a))
# get_vars_Name = lambda args: [name for name in globals() if globals()[name] is args][0]


# 装饰器实现函数运行计时器
def timer(func):
    @wraps(func)
    def core_timer(*args, **kwargs):
        t0 = time.time()
        # print(f"Start: {func.__name__} @{t0}")
        result = func(*args, **kwargs)
        t1 = time.time()
        # print(f'End: {func.__name__} @{t1}')
        print(f'CostTime: func#{func.__name__}@{(t1 - t0):.3f}s')  # 格式化时间
        return result
    
    return core_timer


# 上下文管理计时器 - with myTimer():
class myTimer:
    def __enter__(self):
        self.t0 = time.time()
    
    def __exit__(self, *args, **kwargs):
        print(f'CostTime: @{(time.time() - self.t0):.3f}s')


# 上下文追踪 - with Tracker():
class Tracker(PyCallGraph):
    def __init__(self, output_file=None):
        config = Config()
        config.trace_filter = GlobbingFilter(exclude=[
            'pycallgraph.*',
            '*.secret_function',
            'ModuleLockManager.*',
            'FileFinder.*',
            'SourceFilLoader.*'
        ])
        call_func_name = sys._getframe().f_back.f_code.co_name
        call_func_file = sys._getframe().f_back.f_code.co_filename
        func_name = sys._getframe().f_code.co_name
        logger.debug(f"{call_func_name}() call_func_file: {call_func_file}")
        
        if not output_file:
            output_file = f"funcTracker.{call_func_name}.{func_name}.png"
        graphviz = GraphvizOutput(output_file=output_file)
        super().__init__(output=graphviz, config=config)


# 装饰器 - 实现运行调用链追踪
def tracker(func):
    @wraps(func)
    def track(*args, **kwargs):
        config = Config()
        config.trace_filter = GlobbingFilter(exclude=[
            'pycallgraph.*',
            '*.secret_function',
            'ModuleLockManager.*',
            'FileFinder.*',
            'SourceFilLoader.*'
        ])
        call_func_name = sys._getframe().f_back.f_code.co_name
        call_func_file = sys._getframe().f_back.f_code.co_filename
        logger.debug(f"{call_func_name}() call_func_file: {call_func_file}")
        file_name = f"funcTracker.{call_func_name}.{func.__name__}.png"
        graphviz = GraphvizOutput(output_file=file_name)
        with PyCallGraph(output=graphviz, config=config):
            result = func(*args, **kwargs)
        return result
    
    return track


# 打印对象/模块所有属性值
def getAllAttr(_module):
    module_list = dir(_module)
    length = len(module_list)
    result = {
        "attr": {},
        "__": {},
        "method": {},
        "class": {},
        "object": {},
        "module": {},
        "session": {},
        "other": {},
    }
    for i in range(0, length, 1):
        _attrKey = module_list[i]
        if _attrKey != "__builtins__":
            _attrValue = getattr(_module, _attrKey)
            # logger.debug(f"{module_list[i]}: {_attr}")
            if "__" in str(_attrKey):
                result["__"][_attrKey] = str(_attrValue)
            elif "method" in str(_attrValue):
                result["method"][_attrKey] = str(_attrValue)
            elif "class" in str(_attrValue):
                result["class"][_attrKey] = str(_attrValue)
            elif "object" in str(_attrValue):
                result["object"][_attrKey] = str(_attrValue)
            elif "module" in str(_attrValue):
                result["module"][_attrKey] = str(_attrValue)
            elif "session" in str(_attrValue):
                result["session"][_attrKey] = str(_attrValue)
            
            elif not _attrValue or type(_attrValue) in [str, bool, int, float, complex, list, tuple, range, dict, set,
                                                        frozenset, bytes, bytearray, memoryview]:
                result["attr"][_attrKey] = _attrValue
            else:
                logger.debug(f"{_attrKey}: {_attrValue}")
                result["other"][_attrKey] = str(_attrValue)
    
    result = json.dumps(result)
    logger.debug(f"{str(_module)} 所有属性: \n{result}")
    return result


# 突出强调打印
def Highlight(title):
    Print_Scale = 100
    # print(f' {title} '.center(Print_Scale // 2, "="), end="\n\n")
    logger.info(f' {title} '.center(Print_Scale // 2, "="))


# 目录文件夹创建
def mkdir(file_name):
    file_dir = os.path.dirname(file_name)
    # print(os.path.dirname(file_name))
    if not os.path.exists(file_dir):
        os.makedirs(f"{file_dir}")


# 装饰器 - 实现运行调用链追踪
# def lazy(func):
#     @wraps(func)
#     def lazy(*args, **kwargs):
#
#         result = func(*args, **kwargs)
#         return result
#     return lazy


# 类装饰器 - 类属性 @property 加强版，仅调用一次，固定属性值
# 应用与接口响应结果保存为属性值
class lazy(object):
    def __init__(self, func):
        self.func = func
    
    # 类方法调用装饰器
    # def __call__(self, *args, **kwargs):
    #     return self.func(*args, **kwargs)
    
    def __get__(self, instance, cls):
        val = self.func(instance)
        setattr(instance, self.func.__name__, val)
        return val


# # 类方法调用装饰器 - ?
class setApi(object):
    def __init__(self, func):
        self.func = func
    
    def __get__(self, cls, instance):
        val = self.func(instance)
        # setattr(instance, self.func.__name__, val)
        # setattr(instance, reqs_target, val)
        return val
    
    # 类方法调用装饰器
    def __call__(self, *args, **kwargs):
        val = self.func(*args, **kwargs)
        reqs_target = args
        return self.func(reqs_target)


# 转换字典成为对象 - 01 可以用"."方式访问对象属性
class Objectionary(dict):
    __name__ = "myObjectionary"
    __setattr__ = dict.__setitem__
    __getattr__ = dict.__getitem__
    
    # def __call__(self, *args, **kwargs):
    #     return self.func(*args, **kwargs)
    
    # 不能进行初始化 ！转换字典对象需要
    # def __init__(self, file_path):
    #     super().__init__()
    #     self._sourceData = loadYaml(file_path)
    
    # @staticmethod
    def finder(self, path_list, root_data=None):
        if root_data:
            root = root_data
        else:
            root = self  # 本身对象
        for path in path_list:
            # print("root", root)
            # root = getattr(root, path)
            root = root.get(path)
            if not root:
                logger.error(f"{path_list} 路径中，未找到 {path}\n{self.keys()}")
                raise Exception("Objectionary.finder() 路径数据异常")
        return root
    
    # do 回溯获取调用方 dict 沿用异常调用处理
    # def ensure(self):
    #     back = traceback.extract_stack()
    #     logger.error(f"Objectionary 对象数据为空：{back}")


# 转换字典对象 - 02
class DictObjection:
    # def __init__(self):
    #     self.dictObject = self.dictObject(dictObj)
    
    # 转换字典对象 - 02
    @classmethod
    def transferDict(cls, dictObj):
        _inst = Objectionary()
        # 仅处理 dict 类型
        if isinstance(dictObj, dict):
            # t = 0
            for key, val in dictObj.items():
                _inst[key] = cls.transferDict(val)
                # t += 1
            # print(t)
            return _inst
        # 03/18 新增处理 list 类型 | 保留原 list 类型
        # elif isinstance(dictObj, list):
        #     for index, data in enumerate(dictObj):
        #         # error - Obj.0 SyntaxError: invalid syntax
        #         _inst[f"index{index}"] = cls.transferDict(data)
        #     return _inst
        else:
            return dictObj


# def dictObject(dictObj):
#     if not isinstance(dictObj, dict):
#         return dictObj
#     _inst = Objectionary()
#     # t = 0
#     for key, val in dictObj.items():
#         _inst[key] = dictObject(val)
#     #     t += 1
#     # print(t, _inst)
#     return _inst


"""
文件数据操作 - 类
todo 实例化数据文件（csv / yml / xls）判断文件类型 通用getData 方法
"""


# 0.1 cacheData 缓存流转数据 - import后 仍是当前路径
def cacheData(current_dir, resp_data, target_path, target_key):
    cacheLinkFile = f"{current_dir}/cacheData.yml"
    if not os.path.exists(f"{cacheLinkFile}"):
        dumpYaml(cacheLinkFile, {})
    #     os.makedirs(f"{cacheLinkFile}")
    
    _target = jsonpath(resp_data, target_path)
    if _target:
        logger.debug(f"更新缓存记录数据: {target_key}: {_target[0]}")
        updateCache(cacheLinkFile, {target_key: _target[0]})
        # _cache = loadYaml(cacheLinkFile)
        # _cache.update({target_key: _target[0]})
        # dumpYaml(cacheLinkFile, _cache)
    else:
        logger.error(f"未找到目标数据 {target_key}: {target_path}! 响应结果:\n{resp_data}")


# 1.0 update 更新缓存数据
def updateCache(file_path, new_keys):
    _cache = loadYaml(file_path)
    _cache.update(new_keys)
    dumpYaml(file_path, _cache)


# yaml文件读写操作 返回修改结果
def loadYaml(file_name):
    # 读取文件
    with open(file_name, 'rb') as f:
        # 获取所读取文件中的值
        # all_data = list(yaml.safe_load_all(f)) # --- list[0] -> dict
        all_data = list(yaml.safe_load_all(f))[0]  # --- list[0] -> dict
        # 修改yml文件中的参数
        # all_data["987test"] = 'test01123'   # 追加
        # print(all_data)
    return all_data


# 将json串写入文件
def dumpYaml(file_name, data):
    mkdir(file_name)
    with open(file_name, "w+", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True)  # 正常显示中文字符
    f.close()


# 格式化输出数据 json / yaml
def prettyData(content, _indent=4, _type="json"):
    # 输入限制 Highlight("Output Result ...")
    if not content:
        return False
    try:
        if not isinstance(content, dict):
            if _type == "json":
                # content = json.loads(content)
                content = yaml.safe_load(content)
            else:
                content = yaml.safe_load(content)
        
        if _type == "json":
            result = json.dumps(content, sort_keys=True, indent=_indent, ensure_ascii=False)
        else:
            # yml = yaml.dump(content, default_flow_style=False, allow_unicode=True, default_style='"')
            result = yaml.dump(content, indent=_indent, default_flow_style=False, allow_unicode=True)
        # logger.debug(result)
        return result
    
    except Exception as err:
        logger.error(f"数据格式异常, 无法打印! type: {type(content)}\n{content}")
        logger.error(err)
        return False


"""
csv 文件数据操作
"""


# 只在第一行写入标题,不重复
def csvRecoder(file_name, msg, title=None, _type="w"):
    mkdir(file_name)
    # file_name = f"{Project_Dir}/TestData/indexValueName.csv"
    with open(file_name, _type, newline='', encoding="utf-8") as cfile:
        pen = csv.writer(cfile, delimiter=',')
        # 读取文件判断有无内容行
        with open(file_name, 'r', newline='') as rf:
            reader = csv.reader(rf)
            # if not [row for row in reader]:     # 写入标题
            if title:  # 写入标题
                pen.writerow(title)
                pen.writerows(msg)
            else:
                # for d in data:
                pen.writerows(msg)


# 获取数据
def csvReader(file_name, title=True):
    # file_name = f"{Project_Dir}/TestData/indexValueName.csv"
    result = []
    with open(file_name) as cf:
        lines = cf.readlines()
        # if title:
        #     title_line = lines[0]
        #     for t in title_line:
        #         result.append(t)
        #     for i in lines[1:]:
        #         data_list = i.strip().split(",")
        #         # print(data_li)
        #         _temp = []
        #         for data in data_list:
        #             if "[" in data or "{" in data:
        #                 _temp.append(eval(data))
        #             else:
        #                 _temp.append(data)
        #         result.append(_temp)
        
        for i, line in enumerate(lines):
            data_list = line.strip().split(",")
            # print(data_li)
            _temp = []
            for data in data_list:
                if "[" in data or "{" in data:
                    _temp.append(eval(data))
                else:
                    _temp.append(data)
            result.append(_temp)
    # print(result)
    return result


"""
xls 表格操作
"""

"""
# 读取表格数据 - venderStore(storeInfo)
def xlsRead(sheetname, target, colsIndex=1):

    book = xlrd.open_workbook(index_excel)
    try:
        sheet = book.sheet_by_name(sheetname)
    except:
        logger.error(f"Can not find {index_excel}_{sheetname}!")
        return
    rows = sheet.nrows  # 行
    cols = sheet.ncols  # 列

    for i in range(rows):  # 遍历某列数据
        ctype = sheet.cell_type(i, 0)
        # ctype： 0 empty,1 string, 2 number, 3 date, 4 boolean, 5 error
        # print(ctype)
        key_ = sheet.cell_value(i, 0)  # 定位关键数据列坐标,遍历每行
        # cell = sheet.cell_value(i, 0)  # 定位关键数据列坐标,遍历每行
        # 字符串类型 / 整数类型
        # print(key_, target)
        if ctype == 2 and key_ % 1 == 0:  # 如果是整形
            if int(key_) == int(target):
                logger.debug(sheet.cell_value(i, 1))    # 0 - 首列key, 1 - 名称列
                return sheet.cell_value(i, colsIndex)   # 0 - 首列key, 1 - 名称列
        elif ctype == 3:     # 转成datetime对象
            pass
            date = datetime(*xldate_as_tuple(key_, 0))
            cell = date.strftime('%Y/%d/%m %H:%M:%S')
        elif ctype == 4:    # boolean
            pass
            cell = True if key_ == 1 else False


# 写入表格 v1.0 一次性写入
def xlsWrite_v1(sheetname, list_date):
    book = xlwt.Workbook(encoding='utf-8')
    _sheet = book.add_sheet(sheetname)
    row_num = 0     # 行 cols  # 列

    for list_ in list_date:
        for data in list_:
            _sheet.write(row_num, list_.index(data), data)
        row_num += 1

    # book.save(f"{Project_Dir}/TestData/indexValueName.xls")
    book.save(index_excel)


# 写入表格 v2.0 - 重复写入
def xlsWrite(sheetname, list_date):
    if not os.path.exists(index_excel):
        xlsWrite_v1(sheetname, list_date)
    else:
        book = xlrd.open_workbook(index_excel, formatting_info=True)
        _book = xlscopy(book)     # 复制文件并保留格式
        try:
            _sheet = _book.get_sheet(sheetname)     # 已存在
        except:
            _sheet = _book.add_sheet(sheetname)
        row_num = 0     # 行 cols  # 列

        for list_ in list_date:
            for data in list_:
                _sheet.write(row_num, list_.index(data), data)
            row_num += 1

        _book.save(index_excel)
"""


# 通过列表参数定位字典值
def locateDict(dic, locators, modify, default=None):
    """

    :param dic: 输入需要在其中取值的原始字典 <dict>   整数键值对 -> 不适用
    :param locators: 输入取值定位器, 如:['result', 'msg', -1] <list>
    :param modify: 修改值
    :param default: 进行取值中报错时所返回的默认值 (default: None) -> 定位错误
    :return: 返回根据参数locators找出的值
    """
    # 判断输入值类型
    if not isinstance(dic, dict) or not isinstance(locators, list):
        return default
    value = None  # 申明
    
    # 遍历定位列表
    for loc in locators:
        # 字符串 & 非列表字典 & 非整数索引
        if isinstance(loc, str) and not type(value) in [dict, list] and not isinstance(loc, int):
            try:
                value = dic[loc]
            except KeyError:
                return default
            dic[loc] = modify  # 修改
            continue
        # 嵌套字典迭代
        if isinstance(value, dict):
            try:
                value = locateDict(value, [loc], modify)  # 转list -> 遍历
            except KeyError:
                return default
            # value = modify  # 修改
            continue
        # 嵌套列表与索引
        if isinstance(value, list) and isinstance(loc, int):
            try:
                value = value[int(loc)]
            except IndexError:
                return default
            value[int(loc)] = modify  # 修改
            continue
    
    return dic


# 遍历修改数值
def yaml_travel(data, array=None, text=1, num=1):
    new_data = None
    # 字典
    if isinstance(data, dict):
        new_data = dict()
        for k, v in data.items():
            new_data[k] = yaml_travel(v, array, text, num)
    # 列表
    elif isinstance(data, list):
        new_data = list()
        for item in data:
            item_new = yaml_travel(item, array, text, num)
            if array is None:
                new_data.append(item_new)
            elif len(new_data) < array:
                new_data.append(item_new)
            else:
                pass
    # 字符串
    elif isinstance(data, str):
        new_data = data * text
    # 整数
    elif isinstance(data, int) or isinstance(data, float):
        new_data = data * num
    # 例外
    else:
        new_data = data
    
    return new_data


# 输入/捕获 命令行内容 执行用例结果等
def RunShellWithReturnCode(command, print_output=True, universal_newlines=True):
    out = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True,
                           universal_newlines=universal_newlines)
    
    if print_output:
        output_array = []
        while True:
            line = out.stdout.readline()  # 需要中文转码
            # line = out.stdout.readlines()  # 需要中文转码
            if not line:
                break
            # print(line.strip("/n"))
            output_array.append(line)
        output = "".join(output_array)
        # output = line
    else:
        output = out.stdout.read()
    out.wait()
    errout = out.stderr.read()
    if print_output and errout:
        print(sys.stderr, errout)
    
    out.stdout.close()
    out.stderr.close()
    
    return output, out.returncode


cls_name_list = []


# 扫描项目路径, 自定义用例匹配方法
def myCollecter(path):
    try:
        file_list = os.listdir(path)
    except Exception:
        file_list = []
        print("the path is not dir")
    if file_list:
        for file in file_list:
            file = os.path.join(path, file)
            print(file)
            if os.path.isdir(file):
                myCollecter(file)
            else:
                if file.endswith(".py"):
                    with open(file, encoding="utf-8") as f:
                        for line in f.readlines():
                            cls_match = re.match(r"class\s(.*?)[\(:]", line)
                            if cls_match:
                                cls_name = cls_match.group(1)
                                try:
                                    module = imp.load_source('mycl', file)
                                    cls_a = getattr(module, cls_name)
                                    if cls_a:
                                        cls_name_list.append(cls_name)
                                except:
                                    pass


# 扫描目录下文件
def fileListFunc(filePathList):
    fileList = []
    for filePath in filePathList:
        for top, dirs, nondirs in os.walk(filePath):
            for item in nondirs:
                fileList.append(os.path.join(top, item))
    return fileList


if __name__ == '__main__':
    # if not os.path.exists(record_dater_path):
    #     os.makedirs(record_dater_path)
    pass
    
    # 可用命令行获取总用例数
    # line = os.popen(f"python {pypath}")
    # temp = line._stream.buffer.read().decode(encoding='utf-8')
    # print(temp)
    #
    # reout = re.findall("collected .*? items", temp)[0]
    # print(re.findall(r"[1-9]\d*", reout)[0])   # 匹配正整数
    
    # 遍历匹配
    # for line in f.readlines():    # 正确方式
    # for line in temp:
    #     reout = re.match("collected .*? items", line)
    #     print(reout.group(1))   # 匹配正整数
    
    # print(os.listdir(path_))
