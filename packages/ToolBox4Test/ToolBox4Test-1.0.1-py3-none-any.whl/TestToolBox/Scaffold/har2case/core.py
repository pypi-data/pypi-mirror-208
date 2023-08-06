import base64
import json
import logging
import os
import sys

from Scaffold.har2case import utils
from Scaffold.har2case.compat import urlparse

try:
    from json.decoder import JSONDecodeError
except ImportError:
    JSONDecodeError = ValueError

IGNORE_REQUEST_HEADERS = [
    "host",
    "accept",
    "content-length",
    "connection",
    "accept-encoding",
    "accept-language",
    "origin",
    "referer",
    "cache-control",
    "pragma",
    # "cookie",
    "upgrade-insecure-requests",
    ":authority",
    ":method",
    ":scheme",
    ":path"
]


class HarParser(object):

    def __init__(self, har_file_path, filter_str=None, exclude_str=None):
        self.har_file_path = har_file_path
        self.filter_str = filter_str
        self.exclude_str = exclude_str or ""

    def __make_request_url(self, entry_json):
        """ parse HAR entry request url and queryString, and make teststep url and params

        Args:
            entry_json (dict):
                {
                    "request": {
                        "url": "https://httprunner.top/home?v=1&w=2",
                        "queryString": [
                            {"name": "v", "value": "1"},
                            {"name": "w", "value": "2"}
                        ],
                    },
                    "response": {}
                }

        Returns:
            {
                "name: "/home",
                "request": {
                    url: "https://httprunner.top/home",
                    params: {"v": "1", "w": "2"}
                }
            }

        """

        request_params = utils.convert_list_to_dict(
            entry_json["request"].get("queryString", [])
        )

        url = entry_json["request"].get("url")
        if not url:
            logging.exception("url missed in request.")
            sys.exit(1)

        parsed_url = urlparse.urlparse(url)
        if request_params:
            parsed_object = parsed_url._replace(query='')

        return url, parsed_url

    def __make_request_method(self, entry_json):
        """ parse HAR entry request method, and make teststep method.
        """
        method = entry_json["request"].get("method")
        if not method:
            logging.exception("method missed in request.")
            sys.exit(1)

        return method

    def __make_request_headers(self, entry_json):
        """ parse HAR entry request headers, and make teststep headers.
            header in IGNORE_REQUEST_HEADERS will be ignored.

        Args:
            entry_json (dict):
                {
                    "request": {
                        "headers": [
                            {"name": "Host", "value": "httprunner.top"},
                            {"name": "Content-Type", "value": "application/json"},
                            {"name": "User-Agent", "value": "iOS/10.3"}
                        ],
                    },
                    "response": {}
                }

        Returns:
            {
                "request": {
                    headers: {"Content-Type": "application/json"}
            }

        """
        teststep_headers = {}
        for header in entry_json["request"].get("headers", []):
            if header["name"].lower() in IGNORE_REQUEST_HEADERS:
                continue

            teststep_headers[header["name"]] = header["value"]

        if teststep_headers:
            return teststep_headers
        else:
            return {"version": "5.0.8"}

    def _make_request_data(self, entry_json):
        """ parse HAR entry request data, and make teststep request data

        Args:
            entry_json (dict):
                {
                    "request": {
                        "method": "POST",
                        "postData": {
                            "mimeType": "application/x-www-form-urlencoded; charset=utf-8",
                            "params": [
                                {"name": "a", "value": 1},
                                {"name": "b", "value": "2"}
                            }
                        },
                    },
                    "response": {...}
                }


        Returns:
            {
                "request": {
                    "method": "POST",
                    "data": {"v": "1", "w": "2"}
                }
            }

        """
        method = entry_json["request"].get("method")
        if method in ["POST", "PUT", "PATCH"]:
            postData = entry_json["request"].get("postData", {})
            mimeType = postData.get("mimeType")

            # Note that text and params fields are mutually exclusive.
            if "text" in postData:
                post_data = postData.get("text")
            else:
                params = postData.get("params", [])
                post_data = utils.convert_list_to_dict(params)

            request_data_key = "data"
            if not mimeType:
                pass
            elif mimeType.startswith("application/json"):
                try:
                    post_data = json.loads(post_data)
                    request_data_key = "json"
                except JSONDecodeError:
                    pass
            elif mimeType.startswith("application/x-www-form-urlencoded"):
                post_data = utils.convert_x_www_form_urlencoded_to_dict(post_data)
                print(post_data)
            else:
                # TODO: make compatible with more mimeType
                pass

            return post_data
        else:
            return {}

    def _make_validate(self, teststep_dict, entry_json):
        """ parse HAR entry response and make teststep validate.

        Args:
            entry_json (dict):
                {
                    "request": {},
                    "response": {
                        "status": 200,
                        "headers": [
                            {
                                "name": "Content-Type",
                                "value": "application/json; charset=utf-8"
                            },
                        ],
                        "content": {
                            "size": 71,
                            "mimeType": "application/json; charset=utf-8",
                            "text": "eyJJc1N1Y2Nlc3MiOnRydWUsIkNvZGUiOjIwMCwiTWVzc2FnZSI6bnVsbCwiVmFsdWUiOnsiQmxuUmVzdWx0Ijp0cnVlfX0=",
                            "encoding": "base64"
                        }
                    }
                }

        Returns:
            {
                "validate": [
                    {"eq": ["status_code", 200]}
                ]
            }

        """
        teststep_dict["validate"].append(
            {"eq": ["status_code", entry_json["response"].get("status")]}
        )

        resp_content_dict = entry_json["response"].get("content")

        headers_mapping = utils.convert_list_to_dict(
            entry_json["response"].get("headers", [])
        )
        if "Content-Type" in headers_mapping:
            teststep_dict["validate"].append(
                {"eq": ["headers.Content-Type", headers_mapping["Content-Type"]]}
            )

        text = resp_content_dict.get("text")
        if not text:
            return

        mime_type = resp_content_dict.get("mimeType")
        if mime_type and mime_type.startswith("application/json"):

            encoding = resp_content_dict.get("encoding")
            if encoding and encoding == "base64":
                content = base64.b64decode(text).decode('utf-8')
            else:
                content = text

            try:
                resp_content_json = json.loads(content)
            except JSONDecodeError:
                logging.warning(
                    "response content can not be loaded as json: {}".format(content.encode("utf-8"))
                )
                return

            if not isinstance(resp_content_json, dict):
                return

            for key, value in resp_content_json.items():
                if isinstance(value, (dict, list)):
                    continue

                teststep_dict["validate"].append(
                    {"eq": ["content.{}".format(key), value]}
                )

    def _prepare_teststep(self, entry_json):
        """ extract info from entry dict and make teststep

        Args:
            entry_json (dict):
                {
                    "request": {
                        "method": "POST",
                        "url": "https://httprunner.top/api/v1/Account/Login",
                        "headers": [],
                        "queryString": [],
                        "postData": {},
                    },
                    "response": {
                        "status": 200,
                        "headers": [],
                        "content": {}
                    }
                }

        """
        # teststep_dict = {
        #     "name": "",
        #     "request": {},
        #     # "validate": []
        # }

        # 0528 - 接口数据结构规范
        testapi_dict = self.__make_request_url(entry_json)

        # self.__make_request_url(teststep_dict, entry_json)
        self.__make_request_method(testapi_dict, entry_json)
        self.__make_request_headers(testapi_dict, entry_json)
        self._make_request_data(testapi_dict, entry_json)
        # self._make_validate(testapi_dict, entry_json)

        return testapi_dict

    def _prepare_config(self):
        """ prepare config block.

        """
        return {
            "name": "testcase description",
            "variables": {}
        }

    def _prepare_teststeps(self, fmt_version):
        """ make teststep list.
            teststeps list are parsed from HAR log entries list.

        """

        def is_exclude(url, exclude_str):
            exclude_str_list = exclude_str.split("|")
            for exclude_str in exclude_str_list:
                if exclude_str and exclude_str in url:
                    return True

            return False

        teststeps = []
        log_entries = utils.load_har_log_entries(self.har_file_path)
        for entry_json in log_entries:
            url = entry_json["request"].get("url")
            if self.filter_str and self.filter_str not in url:
                continue

            if is_exclude(url, self.exclude_str):
                continue

            if fmt_version == "v1":
                teststeps.append(
                    {"test": self._prepare_teststep(entry_json)}
                )
            else:
                # v2
                # teststeps.append(
                #     self._prepare_teststep(entry_json)
                # )
                teststeps = self._prepare_structure(entry_json)

        return teststeps

    # 0528 - 接口数据结构规范
    def _prepare_structure(self, entry_json):
        # todo 多接口场景混合

        # 0528 - 接口数据结构规范
        testapi_dict = {
            "CASE_DATA": {},
            "TEMP_HOST": "",
            "TEMP_HEADERS": self.__make_request_headers(entry_json)
        }

        request_query = utils.convert_list_to_dict(
            entry_json["request"].get("queryString", [])
        )

        url, parsed_url = self.__make_request_url(entry_json)

        testapi_dict["TEMP_HOST"] = parsed_url.hostname

        testapi_dict[f"{parsed_url.path}"] = {
            "URL": url,
            "PATH": parsed_url.path,
            "METHOD": self.__make_request_method(entry_json),
            "QUERY": request_query,
            "PARAM": self._make_request_data(entry_json),
            "RESPONSE": ""
        }

        host_name = parsed_url.hostname.split('.')[0]
        # api_name = parsed_url.path

        # return testapi_dict
        return {
            "STRUCTURE": {
                f"{parsed_url.hostname}": {
                    "sysHost": host_name,
                    "API": [parsed_url.path]
                }
            },
            # , "sysHost": apiList
            host_name: testapi_dict
        }

    def _make_testcase(self, fmt_version):
        """ Extract info from HAR file and prepare for testcase
        """
        logging.debug("Extract info from HAR file and prepare for testcase.")

        # config = self._prepare_config()
        # config = self._prepare_structure()
        teststeps = self._prepare_teststeps(fmt_version)

        if fmt_version == "v1":
            testcase = []
            # testcase.append(
            #     {"config": config}
            # )
            testcase.extend(teststeps)
        else:
            # v2
            # testcase = {
            #     # "config": config,
            #     "teststeps": teststeps
            # }

            testcase = teststeps

        return testcase

    def gen_testcase(self, file_type="JSON", fmt_version="v1"):
        harfile = os.path.splitext(self.har_file_path)[0]
        output_testcase_file = "{}.{}".format(harfile, file_type.lower())

        logging.info("Start to generate testcase.")
        testcase = self._make_testcase(fmt_version)
        # logging.debug("prepared testcase: {}".format(testcase))

        if file_type == "JSON":
            utils.dump_json(testcase, output_testcase_file)
        else:
            utils.dump_yaml(testcase, output_testcase_file)
