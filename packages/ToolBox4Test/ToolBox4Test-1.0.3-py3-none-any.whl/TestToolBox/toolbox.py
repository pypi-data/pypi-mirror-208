#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Author    : Gavin
@DateTime  : 2021/3/9 10:35
@Contact   : wen.guo@foxmail.com

@Project   : TestToolbox
@File      : toolbox.py
@Describe  : Test Toolbox | 测试工具箱
————————————————————
@Version   : 1.0.1
"""
# 环境依赖:
# pip install jsonpath
# pip install yaml
#
# update   : 03/10 测试工具箱 1.1
# 1. 数据格式化
# 2. 搜索关键词
# 3. 埋点数据解析 logman
# ————————————————————
# update   :
# 1. do 接口请求响应数据解析
# 2. do 测试数据快速构造
# 3.
# 4.
# ————————————————————
# update   : 23/05/05
# 1. Beta 功能
# 2.
# ————————————————————
# update   :
# 1.
# 2.
# ————————————————————

import sys
import os
import itertools

import time
import datetime
import calendar

import base64
import gzip
import re
import urllib.parse

import json
import yaml
from jsonpath import jsonpath


# 相对路径
# Project_Dir = os.path.dirname(os.path.abspath(__file__))
# sys.path.append(Project_Dir)

# globalSetting暂存
# do 项目全局配置 do 相对路径
# Project_Dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#
# if os.path.relpath(Project_Dir) != ".":
#     os.chdir("../")

"""
Base - 基础录入数据处理
"""


# 中断循环 quit 输入方法
def _input(quit="quit"):
    data = input()
    if data == str(quit):
        main()
    else:
        return data


# cmd 多行录入方法
def get_char(end='end', end_char='', yaml=False):
    data = end
    print("# Tips - (在新行输入 end 停止录入)", end="\n\n")
    while 1:
        var = _input()
        if var == str(end):
            break
        elif end_char != '' and var.find(end_char) != -1:
            var = var[0:var.find(end_char)]
            data = f'{data}\n{var}'
            break
        else:
            data = f'{data}\n{var}'
    result = data.replace(f'{end}\n', '')
    result = result.replace("\t", "")  # 去除换行
    if not yaml:
        result = result.replace("\n", "")  # 去除换行 (yaml 严格格式要求 不能去重换行)
    return result


# read txt 读取文件
def readtxt(file_name):
    with open(file_name, "r", encoding="utf-8") as f:
        for line in f.readlines():
            content = line.strip('\n')  # 去掉列表中每一个元素的换行符
            print(line)
    return content


# yaml文件读写操作 返回修改结果
def loadYaml(file_name):
    # 读取文件
    with open(file_name, 'rb') as f:
        # 获取所读取文件中的值
        # all_data = list(yaml.safe_load_all(f)) # --- list -> list[dict{}]
        all_data = list(yaml.safe_load_all(f))[0]  # --- list[0] -> dict{}
    
    return all_data


# 成对分隔列表 切片组成字典
def zipList2Dict(text_split):
    # # 奇数偶数切片组成字典
    text_key = text_split[::2]  # 奇数index
    text_value = text_split[1::2]  # 偶数index
    
    mod_value = []
    # 解决 value str格式问题
    for val in text_value:
        try:
            mod_value.append(json.loads(val))  # param = "{}"
        except:
            mod_value.append(val)
            # tips(f"json.loads(val)异常: \n{val}")
    
    # 组装成字典
    # text_dict = dict(zip(text_key, text_value))   # value 为 str格式
    text_dict = dict(zip(text_key, mod_value))
    
    return text_dict


# 更新嵌套json串
def myUpdate(nestData, new):
    if isinstance(nestData, dict):
        for nestkey, nestval in nestData.items():  # 遍历一层字典键
            for _k, _v in new.items():
                # logger.debug(f"更新对象键值对: {_k}: {_v}\n匹配键值: {nestkey}: {nestval}")
                if nestkey == _k:
                    # logger.debug(f"判断数据类型: {type(nestval)} == {type(_v)}")
                    if type(nestval) == type(_v):  # val 数据类型相同
                        nestData.update({_k: _v})
                    # elif isinstance(nestval, list) and isinstance(_v, str):
                    elif isinstance(nestval, list):
                        nestval.append(_v)
                    elif isinstance(nestval, int) and isinstance(_v, str):
                        nestData.update({_k: int(_v)})
                
                else:
                    myUpdate(nestval, new)
    
    # 只遍历嵌套列表 不需要底层数值？
    elif isinstance(nestData, list):
        for nest_i in nestData:
            myUpdate(nest_i, new)
    
    return nestData


# 格式化输出数据 json / yaml
def prettyData(content, _type="json"):
    # 输入限制
    separator("Output Result ...", scale // 2)
    try:
        if _type == "json":
            separator("To Json", scale // 4)
            content = json.loads(content)
            js = json.dumps(content, sort_keys=True, indent=4, ensure_ascii=False)
            print(js)
        else:
            separator("To Yaml", scale // 4)
            # print(type(content))
            content = yaml.safe_load(content)
            
            # yml = yaml.dump(content, default_flow_style=False, allow_unicode=True, default_style='"')
            yml = yaml.dump(content, indent=4, default_flow_style=False, allow_unicode=True)
            print(yml)
    
    except Exception as err:
        tips("无法打印!")
        print(err)


# 字符间隔长度
scale = 100


# tips 命令行输出提示
def tips(data="", len=scale // 2):
    print(f"\n# Tips - {data} ", end="\n\n")


def separator(data="", len=scale):
    print("")
    print(f" {data} ".center(len, "="), end="\n")


# 分割请求param参数 -> 字典
def splitParam2Dict(reqs_param):
    # reqs_text = flow.request.get_text()
    reqs_text = reqs_param
    reqs_text = urllib.parse.unquote(reqs_text, encoding='utf-8', errors='replace')
    print(f"\n# raw_reqs_text: \n{reqs_text}")
    
    reqs_text = reqs_text.replace("+", " ")
    # logger.debug(f"reqs_text: \n{reqs_text}")
    
    # # 遍历切割请求数据参数
    try:
        split = reqs_text.split("&")
        text_split = []
        for t in split:
            text_split.extend(t.split("=", 1))  # 加密字段末尾 == 问题 -> split(, num分割次数=1)
            # logger.debug(text_split)
    except Exception as err:
        text_split = reqs_text.split("=", 1)  # 加密字段末尾 == 问题 -> split(, num分割次数=1)
    
    # # 奇数偶数切片组成字典
    text_key = text_split[::2]  # 奇数index
    text_value = text_split[1::2]  # 偶数index
    
    mod_value = []
    # 解决 value str格式问题
    for val in text_value:
        try:
            # if isinstance(val, dict) or isinstance(val, list):
            mod_value.append(json.loads(val))
        except:
            if val:
                mod_value.append(val)
                # print(f"json.loads(val)异常: {val}\n{text_value}")
            else:
                mod_value.append(None)
                print(f"json.loads(val)为空异常: mod_value.append(None)")
    
    # # 组装成字典
    # text_dict = dict(zip(text_key, text_value))   # value 为 str格式
    text_dict = dict(zip(text_key, mod_value))
    
    return text_dict


"""
Func - 测试工具功能方法
"""


# Toolbox 类
class Toolbox:
    # def __init__(self):
    # self.getIn = _input()
    
    # 模式选择
    def choseMode(self, target):
        return getattr(self, target)
    
    # 00 - logman 解析埋点数据
    def ParserLogman(self, debug=None):
        separator("Parser Logman ...")
        tips("请输入待解析埋点 logman 数据:")
        if debug:
            content = debug
        else:
            content = _input()
        # url字符处理
        resource = urllib.parse.unquote(content, encoding='utf-8', errors='replace')
        
        # 判断是否包含 data 是否进行分隔处理
        if "data=" in resource:
            _res = resource.split("&")
            # print(f"切分后数据列表: {_res}")
            
            text_split = []
            for i in _res:
                text_split.extend(i.split("=", 1))
            
            # 成对列表组成字典
            _split = zipList2Dict(text_split)
            
            # 公共处理
            _data = base64.b64decode(_split["data"].encode('utf-8'))
            
            # 判断是否 gzip 解码
            if _split["gzip"] == 1:
                result = gzip.decompress(_data).decode('utf-8')
                # print("gzip解码: " + result)
            else:
                result = _data
        else:  # 仅data字段
            # print(f"error! {resource}")
            _data = base64.b64decode(resource.encode('utf-8'))
            if "H4sIAAAAA" in content:
                result = gzip.decompress(_data).decode('utf-8')
                # print("gzip解码: " + result)
            else:  # 测试环境 gzip=0
                result = _data
                # print(type(result))
        
        if isinstance(result, bytes):  # bytes to str
            result = result.decode()
        
        # print(type(result))
        tips("埋点logman数据解析结果:")
        print(result)
        prettyData(result)
    
    # 11 - Yaml, Json格式化输出 json 输出格式化字典
    def FormatJson(self, type="json"):
        separator(f"Format {type} ...")
        tips("请输入待格式化数据:")
        # content = input()
        content = _input()
        
        # content = json.loads(content)
        tips(f"输出格式化 {type} 数据:")
        prettyData(content, type)
    
    # 12 - yaml 格式化输出
    def FormatYaml(self, type="yaml"):
        separator(f"Format {type} ...")
        tips("请输入待格式化数据:")
        # content = input()
        content = _input()
        
        # content = yaml.safe_load(content)
        tips(f"输出格式化 {type} 数据:")
        prettyData(content, type)
    
    # 11a - 压缩折叠Json
    def StringJson(self):
        separator('Folder JsonData ...')
        tips("请输入格式化Json数据:")
        cont = get_char()
        
        separator("Output Result ...", scale // 2)
        try:
            result = json.loads(cont)
            print(json.dumps(result, ensure_ascii=False))
        except Exception as err:
            tips("数据解析错误!")
            print(err)
    
    # 11b - 压缩折叠Json to yaml
    def StringJson2Yaml(self):
        separator('Folder JsonData ...')
        tips("请输入格式化Json数据:")
        cont = get_char()
        
        separator("Output Result ...", scale // 2)
        try:
            tips(f"输出格式化 {type} 数据:")
            prettyData(cont, "yaml")
        except Exception as err:
            tips("数据解析错误!")
            print(err)
    
    # 12a - 压缩折叠 yaml
    def StringYaml(self):
        separator('Folder YamlData ...')
        tips("请输入格式化Yaml数据:")
        cont = get_char(yaml=True)
        
        separator("Output Result ...", scale // 2)
        try:
            result = yaml.safe_load(cont)
            # print(yaml.dump(result, default_style='"', allow_unicode=True))   # 多行
            # print(result)   # 单引号
            print(json.dumps(result, ensure_ascii=False))
        except Exception as err:
            tips("数据解析错误!")
            print(err)
    
    # 22 - 输入数据 搜索关键词数据
    def SearchKey(self):
        separator('Search JsonData ...')
        tips("请输入搜索关键词:")
        searchKey = _input()
        
        # 命令行输入
        # content = input()
        # tips(f"确定搜索目标关键词: {searchKey}")
        separator("Input JsonData ...", scale // 2)
        tips(f"请输入搜索源数据内容:")
        content = get_char()
        
        # 数据类型转换
        content = yaml.safe_load(content)
        # print(f"{type(content)}\n\n{content}")
        
        result = jsonpath(content, f"$..{searchKey}")
        separator("Output Result ...", scale // 2)
        tips(f"搜索关键词 {searchKey} 返回结果:")
        print(result)
    
    # 31 - 构造模式 - 更新测试数据 myUpdate() 更新嵌套json串
    def myUpdatePro(self):
        separator('myUpdate ...')
        tips("请输入待更新原始数据 (dict{}):")
        _origin = get_char()
        origin = yaml.safe_load(_origin)
        
        separator("Input JsonData ...", scale // 2)
        tips("请输入需更新内容 (dict{}):")
        _target = get_char()
        target = yaml.safe_load(_target)
        
        separator("Output Result ...", scale // 2)
        result = myUpdate(origin, target)
        print(json.dumps(result, sort_keys=True, ensure_ascii=False), end="\n\n")
        # print(json.dumps(result, sort_keys=True, indent=2, ensure_ascii=False))
    
    # 33 - iter() 获取测试数据笛卡尔积
    def iterSimpleKeys(self):  # ["keyword", "pageNum"] -> nestlist: [{case1}, {case2}]
        """
        {"keyName": ["1", "2"], "keyword": ["酸奶","牛奶"]}
        """
        separator('Iter Testdata ...')
        tips("请输入测试数据键值列表 - {k1: [v1, v2], k2: v3}:")
        content = get_char()
        try:
            content = yaml.safe_load(content)
            # content = json.dumps(content, ensure_ascii=False)
        except Exception as err:
            tips("数据解析错误!")
            print(err)
        
        # print(f"content: {content}")
        
        dataPool = []  # [[v1, v2], [v3]]
        keyList = []
        valueList = []  # [(v1, v3), (v2, v3)]
        caseList = []
        for k in content.keys():
            keyList.append(k)
            dataPool.append(content.get(k))  # [[v1, v2], [v3]]
        
        for item in itertools.product(*dataPool):
            # print(f"item: {item}")
            valueList.append(item)  # [(v1, v3), (v2, v3)]
        
        # 拼接成字典  -> [{key1:case1}, {key2:case2}]
        for val in valueList:
            casedict = dict(zip(keyList, val))
            # print(casedict)
            caseList.append(casedict)  # [{k1:v1, k2:v3}, {k1:v2, k2:v3}]
        
        separator("Output Result ...", scale // 2)
        tips(f"生成测试用例数据:")
        print(caseList)
        return caseList
    
    # 34 - 汇总笛卡尔积 - 合并关联key和普通key [{case1}, {case2}], [{case1}, {case2}] -> []
    def iterPro(self, *testKwList, combine=True):
        """
        [{k1:v1, k2:v3}, {k1:v2, k2:v3}] ; [{a:1}, {b:2}] => [{k1:v1, k2:v3, a:1} ...]
        """
        separator('Iter Testdata Pro ...')
        tips("合并多个笛卡尔积结果:")
        
        times = input("请输入待合并列表个数：\n")
        _tempList = []
        for t in range(int(times)):
            _temp = self.iterSimpleKeys()
            tips(f"第 {t} 次数据生成")
            _tempList.append(_temp)
        
        # print(_tempList)    # 输入列表变量
        
        resultList = []
        resultNest = []
        for item in itertools.product(*_tempList):
            resultNest.append(list(item))
            com = {}
            for i in item:  # 重复数据问题 v1.0
                com.update(i)
            resultList.append(com)
        
        separator("Output Result ...", scale // 2)
        tips(f"合并后测试用例数据:")
        print(f"{resultList}")
        if combine:
            return resultList  # -> [{}, {}] / [{ }]
        else:
            return resultNest
    
    # 41 - 当前时间信息
    def nowTime(self):
        separator(f"Format 当前时间 ...")
        print(f"time.time(): \n    {time.time()}\n")
        print(f'time.strftime("%Y-%m-%d %X"): \n    {time.strftime("%Y-%m-%d %X")}\n')
        print(f"time.asctime() %a %b %d %H:%M:%S %Y: \n    {time.asctime()}\n")
        print(f"time.localtime(): \n    {time.localtime()}\n")
        _input()
    
    # 43 - 时间格式 - format时间转时间戳
    def formatTime_format(self):
        separator(f"Format 转换格式化时间 ...")
        print(f"当前时间:\ntime.time(): \n    {time.time()}")
        print(f'time.strftime("%Y-%m-%d %H:%M:%S"): \n    {time.strftime("%Y-%m-%d %X")}')
        tips("请输入待转换格式化时间 (%Y-%m-%d %H:%M:%S):")
        _content = _input()
        try:
            # content = time.strptime(_content, '%Y-%m-%d %H:%M:%S')
            content = time.strptime(_content, '%Y-%m-%d %X')
            print(content)
            result = time.mktime(content)
            tips(f"输出Unix时间戳数据:")
            print(result)
        except:
            tips("数据格式错误! 请输入格式化时间 (%Y-%m-%d %H:%M:%S)!")
    
    # 44 - 时间格式 - Unix时间戳格式化
    def formatTime_unix(self):
        
        separator(f"Format Unix 时间戳格式化 ...")
        print(f"当前时间:\ntime.time(): \n    {time.time()}")
        print(f'time.strftime("%Y-%m-%d %X"): \n    {time.strftime("%Y-%m-%d %X")}')
        
        tips("请输入待格式化Unix时间戳:")
        _content = _input()
        try:
            # 判断时间戳长度, 灵活转化格式
            if len(_content) > 10:
                content = float(int(_content) / 10 ** ((len(_content) - 10)))
                # print(content, len(_content))
            elif len(_content) < 10:
                content = int(int(_content) * 10 ** (10 - len(_content)))
                # print(content, len(_content))
            else:
                content = _content
            result = time.strftime('%Y-%m-%d %X', time.localtime(float(content)))
            tips(f"输出格式化时间数据:")
            print(result)
        except:
            tips("数据格式错误! 请输入数字格式时间戳!")
    
    # 55 - 请求参数 - json 格式化输出
    def formatHTTP_body(self, rawContent=None):
        if rawContent:
            result = splitParam2Dict(rawContent)
            return json.dumps(result, sort_keys=True, ensure_ascii=False)
        
        else:
            separator(f"HTTP请求参数 - json 格式化输出 ...")
            tips("请输入待格式化 请求参数:")
            _content = _input()
            
            result = splitParam2Dict(_content)
            
            tips(f"输出格式化 请求参数:")
            jsonData = json.dumps(result, sort_keys=True, ensure_ascii=False)
            prettyData(jsonData, "json")
            print(jsonData, end="\n\n")
            prettyData(jsonData, "yaml")


"""
主控
"""


# 主控
def main():
    init = """

████████╗███████╗███████╗████████╗    ████████╗ ██████╗  ██████╗ ██╗     ██████╗  ██████╗ ██╗  ██╗
╚══██╔══╝██╔════╝██╔════╝╚══██╔══╝    ╚══██╔══╝██╔═══██╗██╔═══██╗██║     ██╔══██╗██╔═══██╗╚██╗██╔╝
   ██║   █████╗  ███████╗   ██║          ██║   ██║   ██║██║   ██║██║     ██████╔╝██║   ██║ ╚███╔╝
   ██║   ██╔══╝  ╚════██║   ██║          ██║   ██║   ██║██║   ██║██║     ██╔══██╗██║   ██║ ██╔██╗
   ██║   ███████╗███████║   ██║          ██║   ╚██████╔╝╚██████╔╝███████╗██████╔╝╚██████╔╝██╔╝ ██╗
   ╚═╝   ╚══════╝╚══════╝   ╚═╝          ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝╚═════╝  ╚═════╝ ╚═╝  ╚═╝

    Test Toolbox | 测试工具箱 by Gavin

    请输入序号选择测试辅助工具:

    00 - 接口请求响应数据解析
    11 - 数据格式化输出 加解转码
    22 - 搜索关键词数据
    33 - 测试数据构造
    44 - 时间格式处理
    55 - HTTP请求参数格式化

    Tips - (输入 help 查看帮助信息; quit 退出)
    """
    print(init)
    separator("Choose Mode ...", scale // 2)
    
    indexDict = {  # getattr(obj, str)(*args)
        "00": {
            "name": "ParserLogman",
            "desc": "解析模式 - 解析埋点数据:\n(例: H4sIAAAAAAAAAO1...  => {k:v})"
        },
        "11": {
            "name": "FormatJson",
            "desc": "转码模式 - json 格式化输出"
        },
        "11a": {
            "name": "StringJson",
            "desc": "转码模式 - 将多行格式化Json数据, 转换为单行string格式"
        },
        "11b": {
            "name": "StringJson2Yaml",
            "desc": "转码模式 - 压缩折叠Json to yaml"
        },
        "12": {
            "name": "FormatYaml",
            "desc": "转码模式 - yaml 格式化输出"
        },
        "12a": {
            "name": "StringYaml",
            "desc": "转码模式 - 将多行格式化Yaml数据, 转换为单行string格式"
        },
        "22": {
            "name": "SearchKey",
            "desc": "搜索模式 - 批量搜索关键词数据:\n(例: 从响应结果中查询所有sku - key; {key: val} => [vals])"
        },
        "31": {
            "name": "myUpdatePro",
            "desc": "构造模式 - 更新测试数据 myUpdatePro():\n(例: origin: {k1: v1, k2: [{k3: v3}], k3: v4}; target: {k3: tt} => {k1: v1, k2: [{k3: tt}], k3: tt})\n"
        },
        "33": {
            "name": "iterSimpleKeys",
            "desc": "构造模式 - iter() 获取测试数据笛卡尔积:\n(例: {key: [1, 2, 3]} => [{key: 1}, {key: 2}, {key: 3}])"
        },
        "34": {
            "name": "iterPro",
            "desc": "构造模式 - iterPro() 合并多个笛卡尔积结果:\n(例: [{k1:v1, k2:v3}, {k1:v2, k2:v3}] + [{a:1}, {b:2}] => [{k1:v1, k2:v3, a:1} ...])"
        },
        "41": {
            "name": "nowTime",
            "desc": "时间格式 - 当前时间信息\n"
        },
        "43": {
            "name": "formatTime_format",
            "desc": "时间格式 - format时间转时间戳\n"
        },
        "44": {
            "name": "formatTime_unix",
            "desc": "时间格式 - Unix时间戳格式化\n"
        },
        "55": {
            "name": "formatHTTP_body",
            "desc": "请求参数 - json 格式化输出\n"
        },
        # "-": {
        #     "name": "FormatJson",
        #     "desc": "构造模式 - json 格式化输出\n"
        #     },
        # "-": {
        #     "name": "FormatJson",
        #     "desc": "构造模式 - json 格式化输出\n"
        #     },
    }
    
    chose = input()
    
    # print(indexDict.get(chose))
    
    if chose == "quit":
        sys.exit()
    elif chose == "help":
        tips("模式选择帮助信息:")
        print(yaml.dump(indexDict, indent=4, width=120, allow_unicode=True,
                        sort_keys=False))  # ok    , default_style='"' 无换行
        # print(json.dumps(indexDict, indent=2, ensure_ascii=False))
        main()
    elif indexDict.get(chose) is not None:
        tb = Toolbox()
        mode = indexDict.get(chose)
        modeName = mode["name"]
        tips(f"已选择工具 - {modeName}")
        print(f"{mode['desc']}")
        
        while True:
            try:
                tb.choseMode(modeName)()
            except Exception as err:
                tips(f"输入异常!\n{err}")
    
    else:
        tips("未匹配,请重新选择工具模式!")
        main()


if __name__ == '__main__':
    pass
    
    # print(Project_Dir)
    
    # 循环
    # while True:
    #     pprintJson()
    
    # pprintJson()
    
    # 运行程序
    while True:
        main()
    
    # 调试 debug
    # tb = Toolbox()
    # while True:
    #     tb.choseMode("formatHTTP_body")()
    
    # tb.iterSimpleKeys()
    # tb.iterPro()
    # tb.formatHTTP_body()
    
    # tb = Toolbox()
    # tb.ParserLogman(test)
    
    # 页面交互调试
    # from ipywidgets import interact
    # import ipywidgets as widgets
    #
    # widgets.Textarea(
    #     value='Hello World',
    #     placeholder='Type something',
    #     description='',
    #     disabled=False,
    # )
    #
    # widgets.Textarea()
