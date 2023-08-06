#!/usr/bin/python
# -*- coding: UTF-8 -*- 
"""   
@Author    : Gavin
@DateTime  : 2022/6/13 15:17
@Contact   : guowenwhy@foxmail.com

@Project   : TestToolBox
@File      : initRule.py
@Describe  : business_rules 业务规则引擎
————————————————————
@Version   : 0.1 
"""
# update   : 2022/6/13
# 1. business_rules
# 2. v1.5 业务规则数据筛选逻辑层 -- 随机生成合规生产计划
# ————————————————————
# update   : 06/15
# 1. 通用内容参数变量
# 2. 定义行为逻辑
# 3. 加载业务规则配置
# ————————————————————
# update   :
# 1.
# 2.
# ————————————————————
import random

from loguru import logger

from business_rules.actions import BaseActions, rule_action
from business_rules.fields import *
from business_rules.variables import *

from business_rules.engine import run
from business_rules import run_all

from TestToolBox.BaseUtility.iterToolkit import iterTarget2Keys
from TestToolBox.BaseUtility.toolkit import DictObjection, loadYaml, get_varsname
from TestToolBox.Common.initConfig import CSVFactory, CommonConfig

from TestToolBox import Project_Dir


"""
06/13 v1.5 业务规则数据筛选逻辑层 -- 随机生成合规生产计划
"""

RuleMode = "Creation"     # 创造/验证模式 Creation / Validation

# COMMON_ENUM = loadYaml("CMS_COMMON_ENUM.yml")
COMMON_ENUM = CommonConfig(f"{Project_Dir}/Common/CMS_COMMON_ENUM.yml").classData


# 自定义请求参数 - 业务规则校验 - 更新接口请求模板
class CMSContentProduceRule:
    def __init__(self):
        pass
    
    def producePlan(self):
        pass


# 1 - 通用内容参数变量
class ContentVariables(BaseVariables):
    def __init__(self, reqs_params):
        self.vars = reqs_params
    
    # @select_rule_variable(options=["LIVE", "ORCHESTRATION"])
    @string_rule_variable()
    def broadcastType(self):
        return self.vars.broadcastType
    
    @string_rule_variable()
    def produceType(self):
        return self.vars.produceType
    
    @numeric_rule_variable()
    def intensity(self):
        return self.vars.intensity
    
    @select_multiple_rule_variable()
    # @select_rule_variable(options=[1, 2, 131])
    def category(self):
        # logger.info(f"category: {self.vars.category}")
        return self.vars.category
    
    @select_multiple_rule_variable()
    def specificCategory(self):
        return self.vars.specificCategory


# 2 - 行为逻辑
class ContentActions(BaseActions):
    mode = RuleMode
    
    def __init__(self, reqs_params):
        self.vars = reqs_params
    
    @rule_action(params={"intensity": FIELD_NUMERIC})
    def change_intensity(self, intensity, results=None):
        # logger.debug(f"[Rule] 条件匹配结果为 {results}，触发 change_intensity 逻辑")
        if results in [-1, True]:   # not 逆否逻辑 True-1 False-2
            self.vars.update({"intensity": intensity})
        # else:
        
    # @rule_action(params={"broadcastType": FIELD_TEXT})
    def change_broadcastType(self, broadcastType, results=None):
        # logger.debug(f"change_produceType: {results}")
        self.vars.update({"broadcastType": broadcastType})
        
    # @rule_action(params={"produceType": FIELD_TEXT})
    def change_produceType(self, produceType, results=None):
        logger.debug(f"change_produceType: {produceType, results}")
        self.vars.update({"produceType": produceType})
        
    # @rule_action(params={"category": FIELD_SELECT_MULTIPLE})
    @rule_action()
    def limit_category(self, results=None):
        # logger.debug(f"[Rule] 条件匹配结果为 {results}， 触发 limit_category 逻辑")
        _produceType = self.vars.produceType
        _cateLink = COMMON_ENUM.Common.get("category&specificCategory").get("keyValue")
        _limit_category = COMMON_ENUM.ContentRule.produceType.get(_produceType).get("category")
        # Create 模式 -- 可以基于空或单一字段随机生成完整参数
        if self.mode == "Creation":
            self.vars.update({"category": random.choice(_limit_category)})
            self.vars.update({"specificCategory": random.choice(_cateLink.get(self.vars.category[0]))})
            
        # Check Valid 模式 -- 验证完整参数业务逻辑
        else:
            _specificCategory = self.vars.specificCategory
            
            # _limit_category = list(_cateLink.keys())
            if self.vars.category not in _limit_category:
                self.vars.update({"category": random.choice(_limit_category)})
            # 检查层级关联 细分分类
            # _category = self.vars.category
            _limit_specificCategory = _cateLink.get(self.vars.category[0])
            if _specificCategory not in _limit_specificCategory:
                self.vars.update({"specificCategory": random.choice(_limit_specificCategory)})

    @rule_action(params={"assistantCoachIds": FIELD_SELECT})
    def add_assistantCoachIds(self, assistantCoachIds, results=None):
        # logger.debug(f"add_assistantCoachIds: {results}")
        # print(results, assistantCoachIds)
        self.vars.update({"assistantCoachIds": random.sample(assistantCoachIds, 1)})


# 3 - 业务规则
CMS_Rules = CommonConfig(f"{Project_Dir}/Common/CMS_Rules.yml").classData
# producePlan_rule = loadYaml(f"{Project_Dir}/Common/CMS_Rules.yml").get("producePlan_rule")
CMS_Content_Rule = CMS_Rules.CMS_Content_Rule
# producePlan_rule = CMS_Rules.producePlan_rule


# 加载枚举值 随机组合
def genRandomData():
    logger.info("加载枚举值 随机组合")
    # enums = loadYaml("CMS_COMMON_ENUM.yml").get("Common")
    common_enums = COMMON_ENUM.get("Common")
    # 根据场景请求参数 key_list 加载通用枚举值
    scene_keys = COMMON_ENUM.get("ContentRule").get("Scene").get("createProducePlan")
    logger.debug(f"scene_keys: {scene_keys}")
    _temp = {}
    for key in scene_keys:
        if common_enums.get(key):
            _temp.update({key: common_enums.get(key)})
    # 自定义枚举 + 指定参数 {key: [target]}
    # _temp.update({})
    logger.debug(f"_temp: {_temp}")
    
    total_enum = CSVFactory.iterEnum(_temp)
    logger.debug(f"len(): {len(total_enum)}")
    choice = random.sample(total_enum, 5)
    logger.warning(f"随机测试数据列表：\n{choice}")
    random_list = CSVFactory.combineKeysValue(_temp.keys(), *choice)
    logger.info(f"随机测试数据组合：\n{random_list}")
    return random_list


# genRandomData()


def runBizRuleCheck(reqs_data, api_path=None):
    reqs_obj = DictObjection.transferDict(reqs_data)

    if api_path:
        _rules = CMS_Content_Rule.get(api_path)
    else:
        _rules = CMS_Content_Rule.get("common")

    # 过滤无接口规则场景
    if _rules:
        logger.debug(f"[Rule] 请求参数加载业务规则校验: \n{_rules}")
        
        # run 执行业务规则校验
        # one_rule = run(producePlan_rule[3], ContentVariables(reqs_obj), ContentActions(reqs_obj))
        # logger.warning(f"one_rule: {one_rule}")
        
        all_rule = run_all(_rules, ContentVariables(reqs_obj), ContentActions(reqs_obj))
        if not all_rule:
            logger.warning(f"[Rule] 未匹配任意业务规则校验结果: {_rules}")
    
        # logger.info(reqs_obj)
        return reqs_obj
    else:
        return reqs_data


# random_data = genRandomData()
# for reqs in random_data:
#     reqs_obj = runBizRuleCheck(reqs)

# # runBizRuleCheck(random_data)


# demo & debug
def debugRule(reqs_data):
    reqs_obj = DictObjection.transferDict(reqs_data)
    debug_rule = CMS_Content_Rule.debugRule
    
    # run 执行业务规则校验
    one_rule = run(debug_rule[0], ContentVariables(reqs_obj), ContentActions(reqs_obj))
    logger.warning(f"one_rule: {one_rule}")


# debugRule()


"""
Demo 演示
"""

# 本地 import
# import time

# 拼装组合层级关联字段
# combineCate = iterTarget2Keys(COMMON_ENUM.Common, "category&specificCategory")
# print(combineCate)

# 配置文件 自定义函数可变配置
FuncDemo = COMMON_ENUM.FuncDemo
# print(FuncDemo.start)   # lambda *args:f"{time.time()}"
# print(eval(FuncDemo.start))     # <function <lambda> at 0x7fd948b79b80>
# print(eval(FuncDemo.start)())   # 1655435235.427865
# print(type(eval(FuncDemo.start)()))   # <class 'str'>

# print(FuncDemo.end)     # lambda *args:int(time.time())
# print(eval(FuncDemo.end)())   # 1655435235
# print(type(eval(FuncDemo.end)()))   # <class 'int'>

# print(eval(FuncDemo.randomData)())

# 自定义树形规则
demo_rules = COMMON_ENUM.producePlanRule


test_data = {
    "broadcastType": "LIVE",
    # "broadcastType": "ORCHESTRATION",
    "produceType": "KEYFRAME",
    "intensity": 2,
    "category": [
        131
    ],
    "specificCategory": [1]
}

# 请求参数实例化
# _reqs_obj = DictObjection.transferDict(test_data)
# runBizRuleCheck(test_data)

# debugRule(test_data)


# 条件判断
def checkCondition(dataObj, key, symbol, value=None):
    _flag = False
    if symbol == "==":
        if dataObj.get(key) == value:
            return True
    elif symbol == "onlyIn":
        if dataObj.get(key) in value:
            return True
    # elif symbol == "onlyIn":
    return _flag


# 动作执行
def doAction(dataObj, key, symbol, value):
    dataObj.update({key: value})


# 递归解析树形业务规则 -- todo 自定义规则解析引擎
def iterBizRules(dataObj, bizRules):
    for key, grammar in bizRules.items():
        # 必填校验？ 空指针报错？
        logger.debug(f"l1: {key}, {grammar}")
        if dataObj.get(key):
            # 判断是否有下层逻辑
            for symbol, _value in grammar.items():
                logger.debug(f"l2: {symbol}, {_value}")
                # 外层条件
                # if symbol == "onlyIn":
                #     if dataObj.get(key) in _value.keys():
                if checkCondition(dataObj, key, symbol, list(_value.keys())):
                    logger.warning("onlyIn check!")
                    for value, sub in _value.items():
                        # 遍历枚举值
                        logger.debug(f"l3: {value}, {sub}")
                        # 语法规则实现 -- obj条件判断 + 后续执行
                        check_flag = checkCondition(dataObj, key, symbol, value)
                        # if dataObj.get(key) == value:
                        if dataObj.get(key) == value:
                            logger.warning("== check!")
                            # symbol 语法规则判断 -- 执行逻辑/继续下钻
                            if check_flag and sub:    # 1. 判断正确 & 有子规则 - 继续递归检查
                                iterBizRules(dataObj, sub)
                            else:  # 不匹配 & 无子规则 - 依据符号判断是否赋值/取随机
                                doAction(dataObj, key, symbol, value)
                                # dataObj.update({})
                        # 未匹配条件
                        # else:
    logger.info(dataObj)


# iterBizRules(_reqs_obj, demo_rules)


if __name__ == '__main__':
    pass

    # a = random.sample([1, 2], 1)    # -- []
    # print(a)
