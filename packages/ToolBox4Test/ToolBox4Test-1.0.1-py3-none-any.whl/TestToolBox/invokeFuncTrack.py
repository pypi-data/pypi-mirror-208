#!/usr/bin/python
# -*- coding: UTF-8 -*- 
"""   
@Author    : Gavin
@DateTime  : 2020/8/20 11:01
@Contact   : wen.guo@dmall.com

@Project   : TestToolBox
@File      : invokeFuncTrack.py
@Describe  : 
————————————————————
@Version   : 0.1 
"""
# update   : 
# 1.项目内路径使用绝对路径(配置文件中同一调用)
# ————————————————————
# update   : 
# 1.
# ————————————————————

from pycallgraph import PyCallGraph
from pycallgraph import Config
from pycallgraph import GlobbingFilter
from pycallgraph.output import GraphvizOutput

from functools import wraps


# 装饰器 - 实现运行调用链追踪
def tracker(func):
    @wraps(func)
    def track(*args, **kwargs):
        config = Config()
        # config = Config(max_depth=10)
        config.trace_filter = GlobbingFilter(exclude=[
            '*pycallgraph.*',
            # '*.secret_function',
            # 'ModuleLockManager.*',
            # 'FileFinder.*',
            # 'SourceFileLoader.*'
        ])
        out_file = rf'{func.__name__}.trace_detail.png'
        graphviz = GraphvizOutput(output_file=out_file)
        # graphviz = GraphvizOutput(output_type="dot", output_file=out_file)
        with PyCallGraph(output=graphviz, config=config):
            result = func(*args, **kwargs)
        print(f"Function Tracing ... => {out_file}")
        return result
    return track


# 简单追踪
def tarck(func, *args):
    graphviz = GraphvizOutput(output_type="dot", output_file=r'trace_detail.png')
    # graphviz = GraphvizOutput(output_file=r'trace_detail.dot')
    with PyCallGraph(output=graphviz):

        func(*args)


# 过滤/白名单 exclude include
def tarckExclude(func, *args):
    config = Config()
    # 关系图中包括(include)哪些函数名。
    # 如果是某一类的函数，例如类gobang，则可以直接写'gobang.*'，表示以gobang.开头的所有函数。（利用正则表达式）。
    # config.trace_filter = GlobbingFilter(include=[
    #     'main',
    # ])

    # 该段作用是关系图中不包括(exclude)哪些函数。(正则表达式规则)
    config.trace_filter = GlobbingFilter(exclude=[
        'pycallgraph.*',
        '*.secret_function',
        'FileFinder.*',
        'ModuleLockManager.*',
        'SourceFileLoader.*'
    ])
    # graphviz = GraphvizOutput(output_file=r'filter_exclude.png')
    graphviz = GraphvizOutput(output_type="dot", output_file=r'filter_exclude.dot')

    with PyCallGraph(output=graphviz, config=config):
        # os.system("")
        # main_har2case(argv)

        func(*args)


# 控制最大追踪深度
def tarckDeep(func, *args):
    config = Config(max_depth=5)
    graphviz = GraphvizOutput(output_file='filter_max_depth.png')

    with PyCallGraph(output=graphviz, config=config):
        # os.system("")
        # main_har2case(argv)

        func(*args)


if __name__ == '__main__':
    pass

    # tarck()
    # tarckExclude()
    # tarckDeep()

