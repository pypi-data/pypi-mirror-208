#!/usr/bin/python
# -*- coding: UTF-8 -*- 
"""   
@Author    : Gavin
@DateTime  : 2021/6/21 16:29
@Contact   : guowenwhy@foxmail.com

@Project   : TestToolBox
@File      : json2xmind.py
@Describe  : 解析成数据格式 xmind <=> data
————————————————————
@Version   : 0.1 
"""
# update   : 6-21
# 1. xmind 解析
# 2. data 生成 xmind
# 3.
# ————————————————————
# update   : 
# 1. 
# 2. 
# ————————————————————
import json
import xmind
import os
import yaml
from loguru import logger
from xmind.core.markerref import MarkerId


def getFileData(filename):
    ext = os.path.splitext(filename)[1]  # 将文件名路径与后缀名分开
    with open(filename, 'r', encoding='UTF-8') as f:
        if ext == ".json":
            data = json.load(f)
            return data
        elif ext == ".yml" or ext == ".ymal":
            data = list(yaml.safe_load_all(f))[0]
            return data
    # logger.debug("读取json数据\n", data)


# 循环遍历 topics 创建对象
def genXmindByJson(parent, data):
    if data is None:
        return
    node = parent
    # for key in data:
    for key, value in data.items():
        if value:
            if key == 'title':
                # logger.debug(value)
                node.setTitle(value)
            if key == 'link':
                node.setURLHyperlink(value)
            if key == 'note':
                node.setPlainNotes(value)
            if key == 'label':
                node.addLabel(value)
            if key == 'labels':
                for label in value:
                    node.addLabel(label)
            if key == 'comment':
                node.addComment(value)
            if key == 'markers':
                for marker in value:
                    node.addMarker(marker)
            if key == 'topic':   # 画布下 核心主题
                # node.setTitle(data['title'])
                if isinstance(value, dict):
                    genXmindByJson(node, value)
                elif isinstance(value, list):
                    for i in range(len(value)):
                        genXmindByJson(node, value[i])
                else:
                    logger.warning("其它类型")
            if key == 'topics':
                if isinstance(value, dict):
                    genXmindByJson(node, value)
                elif isinstance(value, list):
                    for i in range(len(value)):
                        node = parent.addSubTopic()
                        genXmindByJson(node, value[i])
                else:
                    logger.warning("其它类型")


# 画布 & 主题初始化 - 遍历画布创建 sheet / root 两级遍历
def initSheet(workbook, json_data):
    # 画布主题生成
    def creatTopic(sheet_book, topic_data):
        sheet_book.setTitle(topic_data['title'])    # 画布名称
        _root = sheet_book.getRootTopic()       # 核心主题
        genXmindByJson(_root, topic_data["topic"])
        # 新增 relation 关联创建 - sheet画布曾经统一汇总
        # if topic_data.get("relationships"):
        #     for relate in topic_data["relationships"]:
        #         # todo topicId在重新创建xmind时发生变化,无法使用历史id创建联系
        #         sheet_book.createRelationship(relate["startId"], relate["endId"], relate["title"], )

    # 单画布主题
    if isinstance(json_data, dict):     # 单主题字典
        # return json_data      #
        sheet_ = workbook.getPrimarySheet()
        creatTopic(sheet_, json_data)

    # 多画布, 遍历创建
    elif isinstance(json_data, list):
        sheet0 = workbook.getPrimarySheet()
        creatTopic(sheet0, json_data[0])    # 主画布数据
        for index, sheet in enumerate(json_data[1:]):     # 剩余画布数据遍历
            _sheet = workbook.createSheet()
            creatTopic(_sheet, json_data[index+1])


# 生成 xmind 文件 - json 数据逆向生成
def creatXmind(input_path):
    file_name = os.path.splitext(input_path)[0]
    workbook = xmind.load("temp.xmind")
    _data = getFileData(f"{input_path}")
    # logger.debug(f"加载文件数据 _data: \n{_data}")

    initSheet(workbook, _data)
    xmind.save(workbook, path=f"./{file_name}_json2xmind.xmind")    # 保存xmind


styleDict = {
    "link": "setURLHyperlink",
    "note": "setPlainNotes",
    "label": "addLabel",
    "comment": "addComment",
    "markers": "addMarker"
}


# 解析json数据格式为 yaml 测试用例结构 - 由外而内不可行 逐层update // 由内而外
# content_only 仅节点内容 // 标注信息
def iterXmindJson(json_data, titleKey=None, case_dict=dict(), style=False):
    _split = "#"    # 节点分隔符 . => #

    # style 风格
    def iterStyle(_json_data, _titleKey, _case_dict):
        for key, val in _json_data.items():
            if val and key in ["link", "note", "label", "comment"]:
                # styleKey = f'{_titleKey}{_split}{styleDict[key]}{_split}{val}'
                # _styleKey = {styleKey: None}

                _styleKey = {f'{_titleKey}{_split}{styleDict[key]}': val}
                _case_dict.update(_styleKey)
                # iterXmindJson(val, titleKey, case_dict, style)
            elif key == "markers":  # markers = [] 列表
                for mark in val:
                    styleKey = f'{_titleKey}{_split}{styleDict[key]}{_split}{mark}'
                    _styleKey = {styleKey: None}

                    # _styleKey = {f'{_titleKey}.{styleDict[key]}': mark}
                    _case_dict.update(_styleKey)

    # 同名 同层级 无子主题 topic会被覆盖
    def dealSingle(_json_data, _titleKey, _case_dict):
        _single_val = _case_dict.get(_titleKey)
        if _single_val and isinstance(_single_val, str):  # 有同名 && 为值非字典
            # logger.debug(f"_single_val: {_single_val}")
            _case_dict.pop(_titleKey)
            _case_dict.update({f'{_titleKey}{_split}{_single_val}': None})
            _case_dict.update({f'{_titleKey}{_split}{_json_data["title"]}': None})
        else:
            _titleKey = {_titleKey: _json_data["title"]}
            # titleKey = {titleKey: None}  # do json_data[attr] topic属性配置
            _case_dict.update(_titleKey)

    # todo 新增列表topics子主题 "[]" 
    if isinstance(json_data, list):     # 多画布列表 // 新增列表topics子主题
        for sheet in json_data:
            iterXmindJson(sheet, titleKey, case_dict, style)

    elif isinstance(json_data, dict):   # topic嵌套
        if json_data.get("topic"):      # 核心主题 唯一
            root = json_data["topic"]
            key_val = {root["title"]: {}}
            _nest = {json_data["title"]: key_val}   # sheet: root
            titleKey = f'{json_data["title"]}'
            iterXmindJson(root, titleKey, case_dict, style)
        elif json_data.get("topics"):   # 子主题

            titleKey += f'{_split}{json_data["title"]}'
            if style:
                iterStyle(json_data, titleKey, case_dict)
            for topic in json_data["topics"]:
                iterXmindJson(topic, titleKey, case_dict, style)     # 路径更新

        else:       # 终端无子主题
            # titleKey += f'.{json_data["title"]}'    # do json_data[attr] topic属性配置
            if style:   # 有主题风格
                iterStyle(json_data, titleKey, case_dict)
                dealSingle(json_data, titleKey, case_dict)

            else:       # 无风格标记
                dealSingle(json_data, titleKey, case_dict)

    else:   # style => 终结 style
        logger.error(f"{json_data}, {titleKey}, {case_dict}")
        titleKey = {json_data: None}
        case_dict.update(titleKey)

    return case_dict


# 迭代嵌套字典路径, 生成嵌套字典
def buildNestDict(input_data, key, val):
    _spliter = "#"    # 节点分隔符 . => #

    k_list = key.split(_spliter)
    current = input_data
    # k_list.reverse()      # 倒序列表路径
    for k in k_list[:-1]:

        if isinstance(current, dict):
            if current.get(k):
                current = current[k]
            else:
                current[k] = {}
                current = current[k]
    last_key = k_list[-1]

    # logger.warning(f"current: {current}")
    # logger.error(f"last_key - val: {last_key}: {val}")
    # 短key {b: 2}会覆盖嵌套数据 {a: {b: {c: 3}} - 判断 None再更新
    if current.get(last_key) and isinstance(val, str):
        current[last_key].update({val: None})
    elif current.get(last_key) and isinstance(val, dict):
        current[last_key].update(val)
    else:   # 空字典可更新
        current.update({last_key: val})

    # logger.error(f"input_data: {input_data}")


# Xmind 输出 json
def parserXmind(input_path, type="yml"):
    file_name = os.path.splitext(input_path)[0]
    workbook = xmind.load(f"{input_path}")
    datas = workbook.getData()
    # logger.debug("转化输出json数据", workbook.to_prettify_json())

    # case_data = iterXmindJson(datas)
    case_data = iterXmindJson(datas, style=True)        # 同名 同层级 无子主题 topic会被覆盖
    logger.debug(f"解析Xmind: {json.dumps(case_data, indent=4, ensure_ascii=False)}")

    result = dict()
    for key, val in case_data.items():
        # logger.info(f"遍历: {key}, {val}")
        buildNestDict(result, key, val)
    logger.debug(f"压缩结果: {result}")

    result = {"TestContent": result}
    with open(f"{file_name}_xmind2data.{type}", "w+", encoding="utf-8") as f:
        if type == "yml" or type == "ymal":
            yaml.safe_dump(result, f, allow_unicode=True)        # datas
        elif type == "json":
            json.dump(result, f, ensure_ascii=False)


# 获取结构数据 - 读取 yaml 测试用例结构数据
def get_data(file_path):
    with open(f"{file_path}", "r", encoding="utf-8") as f:
        all_data = list(yaml.safe_load_all(f))[0]
        logger.debug(all_data)
        # logger.debug(json.dumps(all_data, indent=4, ensure_ascii=False))
        # logger.debug(yaml.dump(all_data, allow_unicode=True))
    return all_data


# 根据yaml数据 生成xmind文件
def generateXmind(file_path):
    file_name = os.path.splitext(file_path)[0]
    yaml_data = get_data(file_path)["TestContent"]
    # yaml_data = get_data(file_path)["package"]

    workbook = xmind.load("temp.xmind")

    # 根据结构数据构造xmind
    def _genXmind(root, _datas):
        if isinstance(_datas, dict):
            for key, val in _datas.items():     # topic == dict()
                # 处理 style字段数据
                if key in ["setTopicHyperlink", "setPlainNotes", "addLabel", "addComment"]:
                    content = val
                    getattr(root, key)(content)
                elif key == "addMarker":    # markers = [] 列表
                    for content in [cont for cont in val.keys()]:
                        try:
                            getattr(root, key)(getattr(MarkerId, content))
                        except:
                            getattr(root, key)(content)
                else:
                    topic = root.addSubTopic()
                    topic.setTitle(key)
                    if val:     # do val为值的情况 and type(val) == dict
                        _genXmind(topic, val)
        # 列表数据类型
        elif isinstance(_datas, list):
            for _val in _datas:
                _genXmind(root, _val)

        else:       # null 结尾处理
            # logger.warning(f"root, _datas: {_datas}")
            topic = root.addSubTopic()
            topic.setTitle(_datas)

    for s_key, s_val in yaml_data.items():  # sheet todo 新建/修改文件区分
        # logger.error(f"workbook.getSheets() {workbook.getSheets()}")
        if len(workbook.getSheets()) > 1:    # 多sheet - 新建表不覆盖修改
            sheet = workbook.createSheet()
            sheet.setTitle(s_key)
            for r_key, r_val in s_val.items():  # root 主题 只能添加marker
                root = sheet.getRootTopic()
                root.setTitle(r_key)
                # root.addMarker(MarkerId.starBlue)
                _genXmind(root, r_val)

        else:   # 单sheet  获取默认画布
            sheet1 = workbook.getPrimarySheet()
            sheet1.setTitle(s_key)
            for r_key, r_val in s_val.items():
                root1 = sheet1.getRootTopic()
                root1.setTitle(r_key)
                # getattr(root, "addMarker")(MarkerId.starBlue)
                _genXmind(root1, r_val)

    xmind.save(workbook, path=f'{file_name}_yaml2xmind.xmind')     # 另存为
    # xmind.save(workbook)   # 更新内容


if __name__ == '__main__':
    pass

    # getFileData(rf"../docs/xmind_json_demo.json")

    # xmind 导出规范json格式才能直接生成
    # creatXmind(sys.argv[1])
    creatXmind("raw.json")
    # creatXmind(rf"../docs/xmind_template_v1.1.json")
    # creatXmind(rf"../docs/xmind_testcase_template_v1.1.yml")

    # workbook = xmind.load("xmind_testcase_demo.xmind")
    # workbook = xmind.load("xmind_v1.1.xmind")
    workbook = xmind.load("xmind_v1.1_xmind2data_yaml2xmind.xmind")
    # logger.debug(f"转化Xmind输出dict数据:\n{workbook.getData()}")
    # logger.debug(f"转化Xmind输出json数据:\n{workbook.to_prettify_json()}")
    sheet = workbook.getPrimarySheet()
    logger.debug(f"转化画布输出dict数据:\n{sheet.getData()}")
    logger.debug(f"转化画布输出dict数据:\n{sheet.getData()['relationships']}")

    # 解析 Relationships 关联topic
    # 增加relation节点 \Anaconda3\envs\AutoTestTool\Lib\site-packages\xmind\core\sheet.py
    """
    # new relationships content
    relations = []
    for relation in self.getRelationships():
        relate = {
            "startId": relation.getEnd1ID(),
            "endId": relation.getEnd2ID(),
            "relationTitle": relation.getTitle(),
        }
        relations.append(relate)
    """

    # sheet = workbook.getPrimarySheet()  # 画布
    # sheets = workbook.getSheets()  # 多画布
    # root = sheet.getRootTopic()  # 主题

    # getStructureClass = root.getStructureClass()  # none
    # logger.debug(getStructureClass)

    # Xmind 输出 json
    # parserXmind("../docs/xmind_v1.1.xmind")
    # parserXmind("xmind_v1.1.xmind")
    # parserXmind("miniAST_yaml2xmind.xmind")

    # 直接读取解析结果
    # datas = getFileData("./xmind_template_v1.1.json")
    # # case_data = iterXmindJson(datas)
    # case_data = iterXmindJson(datas, style=True)
    # logger.debug(f"解析Xmind: {case_data}")
    # logger.debug(f"{len(case_data.keys())}")

    # 根据yaml文档数据生成xmind
    # generateXmind("Risk_xmindCase.yml")
    # generateXmind(r"miniAST.json")
    # generateXmind(r"miniAST.yml")
