#!/usr/bin/python
# -*- coding: UTF-8 -*- 
"""   
@Author    : Gavin
@DateTime  : 2022/1/10 12:01
@Contact   : guowenwhy@foxmail.com

@Project   : TestToolBox
@File      : initRequest.py
@Describe  : 接口请求数据初始化 规范化
————————————————————
@Version   : 0.1 
"""
# update   : 2022/1/10
# 1. get、post 请求数据格式化 - 请求数据类
# 2. 
# ————————————————————
# update   : 03/21 API】接口父类 Reqs、Resp 父类、子类优化
# 1.接口文档加载单例模式
# 2.封装接口实例及请求方法
# 3.实现中文接口名称外部调用
# ————————————————————
# update   : 04/06
# 1. 优化底层接口方法，区分 `POST/GET` 请求方式；
# 2. 对应更新 `PARAM/QUERY` 数据
# 3.
# ————————————————————
# update   : 05/09
# 1. 接口请求参数测试数据更新方式 - 变更为 .update()
# 2.
# ————————————————————
# update   : 06/01
# 1. 接口请求 send() 方法新增可配置环境参数 -- _updateURL
# 2.
# ————————————————————
# update   : 06/17
# 1. 【Config】配置动态参数及接口请求参数解析: ` lambda *args:int(time.time()*1000+24*60*60*1000)`
# 2.
# ————————————————————
# update   :
# 1.
# 2.
# ————————————————————
# from typing import Union

# 支持动态参数函数表达 lambda -- import 模块依赖
import json
from jsonpath import jsonpath
from loguru import logger
import random
import re
import requests
from requests import Response

from TestToolBox.BaseUtility.toolkit import DictObjection, Objectionary, Highlight, prettyData
# from BaseUtility.iterToolkit import myUpdatePro
from TestToolBox.Common.initConfig import CommonConfig, CSVFactory
# flag = 0
from TestToolBox.Common.initRule import runBizRuleCheck

from TestToolBox import Project_Dir

COMMON_ENUM = CommonConfig(f"{Project_Dir}/Common/CMS_COMMON_ENUM.yml").classData


# todo 全部继承 父类 CommonConfig
class REQS:     # 接口请求类
    
    # todo 加载接口文档后，统一校验必要字段 REQUEST RESPONSE
    # def __init__(self, api_doc: Objectionary, api_target: Union[str, list],
    #              test_param: dict = None, add_headers: dict = None):
    def __init__(self, api_doc: Objectionary):
        """
接口请求, 通过加载接口文档, 指定目标接口路径, 自动组装、更新请求数据
        :param api_doc: 加载接口文档 Objectionary 对象 - CommonConfig(api_doc).classData 加载接口路径yaml文件
        """
        # 继承 CommonConfig() 类
        # super().__init__(api_doc)
        # self.apiDoc = CommonConfig(api_doc).classData
        # self._origin_file = api_doc
        # 直接使用 Objectionary 对象 - 优化配置加载效率，提高复用率
        self.apiDoc = api_doc
        self.targetApi = None
        # 初始化时即验证数据 03/19改 子类使用 接口名称调用
        # self.reqs_target = api_target
        # self.addHeaders = add_headers
        # self.testParam = test_param
        # self.apiData = self._DATA
        # self.reqsData = self._REQUEST
        # 不重复发起请求
        # self.respData = self.apiData.RESPONSE

    # @setApi
    def _ApiData(self, reqs_target):    # 接口文档数据 # 获取接口文档数据
        # global flag
        # flag += 1
        # print(flag)
        if isinstance(reqs_target, str):
            _target_api = self.apiDoc.get(reqs_target)
        # done 兼容 finder 深度查询模式 [root, api]
        elif isinstance(reqs_target, list):
            _target_api = self.apiDoc.finder(reqs_target)
        else:
            raise Exception(f"文档中未找到接口: {reqs_target}\n{self.apiDoc.keys()}")
        # logger.debug(f"[REQS] 定位文档中接口数据 {self.reqs_target}: \n{_target_api}")
        if _target_api:
            setattr(self, "targetApi", _target_api)
            logger.info(f"[REQS] 成功加载接口: {_target_api.DESC}")
            return _target_api
        else:
            logger.error(f"[REQS] 该定位接口数据为空! {reqs_target}\n{self.apiDoc.keys()}")
            raise Exception("该定位接口数据为空，无法初始化接口配置！")

    # ENUM 字段枚举值
    # @lazy
    @staticmethod
    def _FieldEnum(targetApi):
        return targetApi.ENUM

    # @lazy
    @staticmethod
    def __REQUEST(targetApi):    # 接口文档数据
        # _reqs_data = self.ApiData(reqs_target).REQUEST
        # 优化重复加载配置 和 依赖 reqs_target 传参
        _reqs_data = targetApi.REQUEST
        # setattr(self, "_REQUEST", _reqs_data)
        # logger.debug(f"[REQS] Reqs._REQUEST: {_reqs_data}")
        return _reqs_data

    # @lazy
    @staticmethod
    def __URL(targetReqs):
        # return self._REQUEST.URL
        _url = f"http://{targetReqs.HOST}{targetReqs.PATH}"
        logger.debug(f"[REQS] 加载 REQS._URL: {_url}")
        return _url

    # do 切换环境 - 替换 HOST -- 定制化需求 子类定义？
    @staticmethod
    def _updateURL(targetReqs, env_host):
        fiture_pattern = "(.*?).XXX.com"     # https?://
        if not env_host:
            _url = f"http://{targetReqs.HOST}{targetReqs.PATH}"
            logger.debug(f"[REQS] 加载默认配置 REQS._URL: {_url}")
        elif env_host.lower() in ["qa", "dev"]:
            # *可选【Base】`*ApiDoc.yml` 接口配置新增 应用名称`APP`字段 -- 支持自定义环境切换
            # _host = f"http://stable-{targetReqs.APP}-nt.{env_host.lower()}.fiture.com"
            # _url = _host + targetReqs.PATH
            # 直接替换默认配置域名中环境标识 .qa.
            _host = str(targetReqs.HOST).replace("qa", env_host.lower())
            _url = f"http://{_host}{targetReqs.PATH}"
            logger.debug(f"[REQS] 加载自定义环境配置 {env_host}: {_url}")
        elif re.match(fiture_pattern, env_host):
            # 正则匹配URL域名 https?://(.*?).fiture.com
            if "http" in env_host:
                _url = env_host + targetReqs.PATH
            else:
                _url = "http://" + env_host + targetReqs.PATH
            logger.debug(f"[REQS] 加载自定义域名配置 {env_host}: {_url}")
        else:
            _url = "http://XXX.com" + targetReqs.PATH
            logger.error(f"[REQS] 加载自定义配置 env_host 参数异常: {env_host}")
        return _url

    # @lazy
    @staticmethod
    def __HEADERS(targetReqs):
        return targetReqs.HEADERS
    
    # 缓存登陆 token
    api_cache_file = f"{Project_Dir}/TestSuite_CMS_Api/cacheData.yml"

    @staticmethod
    def _updateHeaders(targetReqs, addHeaders):
        # _headers = copy.deepcopy(dict(self._HEADERS()))
        _headers = dict(targetReqs.HEADERS)
        # logger.info(f"REQS.HEADERS: {_headers}")
        if addHeaders:
            # logger.debug(f"加载 REQS.addHeaders: \n{addHeaders}")
            _headers.update(addHeaders)
            logger.info(f"[REQS] 更新后 REQS.updateHeaders: \n{_headers}")
        return _headers

    # @lazy
    @staticmethod
    def __PARAM(targetReqs):
        return targetReqs.PARAM

    # 依据ENUM枚举字段 获取笛卡尔积 预随机参数
    @staticmethod
    def _genRandomEnum(apiEnum, custom_param=None, nums=1):
        # todo 接口更新全局教练、类目、器材等枚举值
        common_enums = COMMON_ENUM.get("Common")
        # 根据场景请求参数 key_list 加载通用枚举值
        prama_keys = list(apiEnum.keys())
        _temp = {}
        for key in prama_keys:
            if common_enums.get(key):
                _temp.update({key: common_enums.get(key)})
        if custom_param:
            for _key, _value in custom_param.items():
                _temp.update({_key: [_value]})
        # 笛卡尔积
        total_enum = CSVFactory.iterEnum(_temp)
        # logger.debug(f"len(): {len(total_enum)}")
        choice = random.sample(total_enum, nums)
        random_list = CSVFactory.combineKeysValue(_temp.keys(), *choice)
        logger.debug(f"[REQS] 笛卡尔积随机枚举数据列表：\n{random_list}")
        return random_list

    # 更新接口请求参数
    @staticmethod
    def _updateParams(targetReqs, testParams, _type="PARAM"):
        # _reqs_param = copy.deepcopy(dict(self._PARAM()))  # dict 才能deepcopy
        _reqs_param = dict(targetReqs.get(_type))  # dict 才能deepcopy / obj 无需 deepcopy
        # logger.debug(f"[REQS] 加载 REQS.testParams: {testParams}")
        
        if testParams:
            logger.debug(f"[REQS] 加载 REQS.testParams: \n{testParams}")
            # myUpdatePro(_reqs_param, testParams)    # 无法新增
            _reqs_param.update(testParams)
            # _reqs_param = json.dumps(_reqs_param)   # 请求数据 json格式
        
        # 解析处理配置函数 lambda 表达式 -- Rule 业务规则层 创建 & 校验场景
        for key, value in _reqs_param.items():
            if isinstance(value, str) and "lambda" in value:
                _reqs_param.update({key: eval(value)()})
                
        # do 业务规则校验层 -- do 区分不同接口字段 PATH 各自业务规则
        # logger.debug(f"[REQS] 请求参数业务规则校验 _reqs_param: {_reqs_param}")
        _reqs_param = runBizRuleCheck(_reqs_param, targetReqs.PATH)
        
        # 根据 Content-Type 判断请求类型
        if targetReqs.METHOD == "POST":
            if targetReqs.HEADERS.get("Content-Type") == "application/json":
                _reqs_param = json.dumps(_reqs_param)   # 请求数据 json格式

        logger.info(f"[REQS] 请求参数 REQS.updateParams: \n{prettyData(_reqs_param)}")
        return _reqs_param

#     def send(self):
#         """
# 接口请求执行 根据接口文档配置 进行 GET / POST 发起请求
#         :return: 响应结果，可使用 .text 返回纯文本 .json() 返回结构数据
#         """
#         _resp = requests.post(self._URL, self.updateParam(), headers=self.updateHeaders(), verify=False)
#         # logger.info(f"[REQS] Reqs._RESPONSE: {_resp.json()}")
#         logger.debug(f"[REQS] RESP.text: \n{_resp.text}")
#         return _resp

    def _chooseMethod(self, targetReqs, url, headers, test_params=None, apiEnum=None):
        # 依据ENUM枚举字段 获取笛卡尔积 预随机参数
        # random_param = None
        # logger.warning(f"apiEnum: {apiEnum}")
        # if apiEnum:
        #     test_params = self._genRandomEnum(apiEnum, test_params)[0]
        if targetReqs.get("METHOD") == "POST":
            _params = self._updateParams(targetReqs, test_params)
            _resp = requests.post(url, _params, headers=headers, verify=False)
            # return None
        else:
            _querys = self._updateParams(targetReqs, test_params, _type="QUERY")
            _resp = requests.get(url, _querys, headers=headers, verify=False)
        return _resp

    # 发起请求 todo 根据 method 判断请求方式
    def send(self, reqs_target, test_params: dict = None, env_host: str = None, add_headers: dict = None):
        """
接口请求执行 根据接口文档配置 进行 GET / POST 发起请求
        :param reqs_target: 接口请求目标 指定目标接口路径 顶层 str 或 深度 list 搜索
        :param test_params: 测试数据, 将自动更新接口文档中 请求参数
        :param env_host: 环境域名 stable + APP名称 cp-fcc-nt + 环境 dev/qa/prod + fiture.com
        :param add_headers: 请求头数据, 待更新登录认证 token等
        :return: 响应结果，可使用 .text 返回纯文本 .json() 返回结构数据
        """
        Highlight(f"[REQS] 加载接口数据")
        logger.debug(f"[REQS] 接口路径: {reqs_target}")
        # 必要进行初始化 setattr(targetApi)
        _ApiData = self._ApiData(reqs_target)
        targetReqs = _ApiData.REQUEST
        apiEnum = _ApiData.ENUM
        # Highlight(f"{self.targetApi}")
        
        # _url = self.__URL(targetReqs)
        _url = self._updateURL(targetReqs, env_host)
        _headers = self._updateHeaders(targetReqs, add_headers)
        _resp = self._chooseMethod(targetReqs, _url, _headers, test_params, apiEnum)
        
        Highlight(f"[RESP] 获取响应数据: RESP.text")
        logger.debug(f"[RESP] {_resp}\n")
        logger.debug(f"[RESP] {_resp.text}\n")
        return _resp

    # @property
    # def _RESPONSE(self):    # 接口文档数据
    #     # self._REQUEST.METHOD
    #     _resp_result = self.send()
    #     if _resp_result:
    #         _resp_result = _resp_result.json()
    #         logger.debug(f"[REQS] REQS._RESPONSE: \n{_resp_result}")
    #         return Resp(_resp_result)
    #
    # # 获取接口响应结果
    # def getResp(self):
    #     # return self._DATA
    #     return self._RESPONSE


# 响应结果对象 200验证
class RESP(Response):
    def __init__(self, response):
        super().__init__()
        Highlight(f"验证响应结果 response")
        self.respOrigin = response
        self.respData = self._transfer(response)
        self.respFormat = prettyData(self.respData)

    def _transfer(self, response):
        assert self.check_code()
        try:
            _data = response.json()
            if isinstance(_data, dict):
                logger.info(f"[RESP] 响应状态 status_code 200 验证通过 - {response}\n")
                return DictObjection.transferDict(_data)
            else:
                logger.error(f"[RESP] 响应数据 response 异常\n{_data}")
                raise Exception
        except Exception as error:
            logger.error(f"[RESP] 响应数据 resp.json() 异常\n{response}")
            logger.error(error)
            # raise Exception

    def check_code(self):
        _code = self.respOrigin.status_code
        if _code == 200:
            return True
        else:
            logger.error(f"[RESP] 响应状态 status_code 非200异常！\n{self.respOrigin}")
            self.raise_for_status()
            return False

    def _check_equal(self, key, expect):
        _temp = self.respData.get(key)
        
        if _temp:
            if _temp == expect:
                logger.info(f"[RESP] 响应数据 {key} 检查通过 - {expect} == {_temp}")
                return True
            else:
                logger.error(f"[RESP] 响应数据 {key} 检查异常！预期：{expect} != 实际：{_temp}\n{self.respFormat}")
                return False
        else:
            logger.error(f"[RESP] 响应数据 {key} 检查异常！\n{self.respFormat}")
            return False
        
    def _check_not_empty(self, target_key):
        _content = jsonpath(self.respData, f"$..{target_key}")
        if _content:
            # 最终判断_content是否为false，如果为false则表示找不到子节点数据
            if _content is False:
                # 如果返回false，则再次尝试直接寻找当前的节点
                _content = jsonpath(self.respData, f"$.{target_key}")
                logger.info(f"[RESP] 直接检查当前节点结果: {_content}")
                return _content
            # 此次不能使用len判断，len函数只适用于部分数据，对int会报错，只需要判断是否为空即可
            if _content[0] is not None:
                logger.info(f"[RESP] 检查通过 {target_key} 响应数据内容不为空")
                return True
            else:
                logger.error(f"[RESP] 检查异常 响应数据 {target_key} 长度异常！"
                             f"\n{self.respFormat}")
                return False
            # if len(_content[0]) == 0:
            #     logger.error(f"检查异常 响应数据 {target_key} 长度异常！"
            #                  f"\n{self.respFormat}")
            #     return False
            # else:
            #     logger.info(f"检查通过 {target_key} 响应数据内容不为空, 数据对象长度: {len(_content[0].get('records'))}")
            #     return True
        else:
            logger.error(f"[RESP] 检查异常 响应数据 {target_key} 内容异常！\n{self.respFormat}")
            return False

    def _check_empty(self, target_key):
        _content = jsonpath(self.respData, f"$..{target_key}")
        if _content:
            if len(_content[0]) == 0:
                logger.info(f"[RESP] 检查通过 响应数据 {target_key} 长度为 0 , 与预期一致")
                return True
            else:
                logger.error(f"[RESP] 检查异常 {target_key} 响应数据内容不为空, 数据对象长度: {len(_content[0])}\n{self.respFormat}")
                return False
        else:
            logger.info(f"[RESP] 检查通过 响应数据 {target_key} 内容为空, 与预期一致")
            return True


if __name__ == '__main__':
    pass
    # 实例对象
    # apiPath = apiPath.classData
    
    # check pass - jsonpath
    # test_path = jsonpath(apiPath, "$..X-NT-App-Meta")
    # print(test_path)

    # re 正则匹配自定义配置接口域名
