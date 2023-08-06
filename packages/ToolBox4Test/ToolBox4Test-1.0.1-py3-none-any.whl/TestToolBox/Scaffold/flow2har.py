#!/usr/bin/python
# -*- coding: UTF-8 -*- 
"""   
@Author    : Gavin
@DateTime  : 2021/5/26 15:39
@Contact   : wen.guo@foxmail.com

@Project   : AutoTestTool
@File      : flow2har.py
@Describe  : mitmproxy 代理抓包, 生成.har文件
————————————————————
@Version   : 0.1 
"""
# update   : 
# 1. 
# 2. 
# ————————————————————
# update   : 
# 1. 
# 2. 
# ————————————————————


import json
from datetime import datetime
from datetime import timezone

from mitmproxy import proxy, options
from mitmproxy import ctx
from mitmproxy.tools.dump import DumpMaster

# copy.deepcopy


def flow_to_har(flow):
    '''
    将flow转换成har格式数据
    '''

    def fromat_cookies(l):
        return [{'name': i[0], 'value': i[1]} for i in l]

    def name_value(obj):
        return [{"name": k, "value": v} for k, v in obj.items()]

    HAR = {}
    HAR.update({
        "log": {
            "version": "1.2",
            "creator": {
                "name": "mitmproxy har_dump",
                "version": "0.1",
                "comment": "mitmproxy"
            },
            "entries": []
        }
    })

    ssl_time = -1
    connect_time = -1

    if flow.server_conn and flow.server_conn:
        connect_time = (flow.server_conn.timestamp_tcp_setup -
                        flow.server_conn.timestamp_start)

        if flow.server_conn.timestamp_tls_setup is not None:
            ssl_time = (flow.server_conn.timestamp_tls_setup -
                        flow.server_conn.timestamp_tcp_setup)

    timings_raw = {
        'send': flow.request.timestamp_end - flow.request.timestamp_start,
        'receive': flow.response.timestamp_end - flow.response.timestamp_start,
        'wait': flow.response.timestamp_start - flow.request.timestamp_end,
        'connect': connect_time,
        'ssl': ssl_time,
    }

    timings = {
        k: int(1000 * v) if v != -1 else -1
        for k, v in timings_raw.items()
    }

    full_time = sum(v for v in timings.values() if v > -1)

    started_date_time = datetime.fromtimestamp(flow.request.timestamp_start, timezone.utc).isoformat()

    response_body_size = len(flow.response.raw_content) if flow.response.raw_content else 0
    response_body_decoded_size = len(flow.response.content) if flow.response.content else 0
    response_body_compression = response_body_decoded_size - response_body_size

    entry = {
        "startedDateTime": started_date_time,
        "time": full_time,
        "request": {
            "method": flow.request.method,
            "url": flow.request.url,
            "httpVersion": flow.request.http_version,
            "cookies": fromat_cookies(flow.request.cookies.fields),
            "headers": name_value(flow.request.headers),
            "queryString": name_value(flow.request.query or {}),
            "headersSize": len(str(flow.request.headers)),
            "bodySize": len(flow.request.content),
        },
        "response": {
            "status": flow.response.status_code,
            "statusText": flow.response.reason,
            "httpVersion": flow.response.http_version,
            "cookies": fromat_cookies(flow.response.cookies.fields),
            "headers": name_value(flow.response.headers),
            "content": {
                "size": response_body_size,
                "compression": response_body_compression,
                "mimeType": flow.response.headers.get('Content-Type', '')
            },
            "redirectURL": flow.response.headers.get('Location', ''),
            "headersSize": len(str(flow.response.headers)),
            "bodySize": response_body_size,
        },
        "cache": {},
        "timings": timings,
    }

    entry["response"]["content"]["text"] = flow.response.get_text(strict=False)

    if flow.request.method in ["POST", "PUT", "PATCH"]:
        params = [
            {"name": a, "value": b}
            for a, b in flow.request.urlencoded_form.items(multi=True)
        ]
        entry["request"]["postData"] = {
            "mimeType": flow.request.headers.get("Content-Type", ""),
            "text": flow.request.get_text(strict=False),
            "params": params
        }

    if flow.server_conn.connected:
        entry["serverIPAddress"] = str(flow.server_conn.ip_address[0])

    HAR["log"]["entries"].append(entry)

    return HAR


class Test:
    def response(self, flow):
        """
        在response事件中写处理逻辑
        """
        msg = json.dumps(flow_to_har(flow))
        ctx.log.info('flow转化har格式数据')
        ctx.log.info(msg)


if __name__ == "__main__":

    opts = options.Options(listen_host='127.0.0.1', listen_port=8080)
    opts.add_option("body_size_limit", int, 0, "")

    pconf = proxy.config.ProxyConfig(opts)
    m = DumpMaster(None)
    m.server = proxy.server.ProxyServer(pconf)

    m.addons.add(Test())

    try:
        m.run()
    except KeyboardInterrupt:
        m.shutdown()
