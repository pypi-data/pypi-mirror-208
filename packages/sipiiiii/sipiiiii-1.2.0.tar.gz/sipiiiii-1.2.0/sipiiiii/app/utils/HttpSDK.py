# coding: utf-8
try:
    from utils.formatConversion import verify_json, DottableDict
except ImportError:
    from .formatConversion import verify_json, DottableDict

import validators
import httpx
import time


def log_request(request):
    # print(
    #     f"Request event hook: {request.method} {request.url} - Waiting for response")
    pass


def log_response(response):
    request = response.request
    # print(
    #     f"Response event hook: {request.method} {request.url} - Status {response.status_code}"
    # )
    pass


def raise_on_4xx_5xx(response):
    response.raise_for_status()


class HTTP(object):
    def __init__(self, proxies=None):
        pass
        self._proxy = proxies
        if proxies is not None:
            if verify_json(proxies) is True:
                self._proxy = proxies
            else:
                raise Exception(
                    f"proxies not json , header value now :{proxies}")
        self._verify = False
        try:
            self.session = httpx.Client(
                event_hooks={
                    "request": [log_request],
                    "response": [log_response, raise_on_4xx_5xx],
                },
                proxies=self._proxy,
                verify=self._verify
            )
        except Exception as e:
            print(e)

        self._cookie = httpx.Cookies()
        self._timeout = 60
        self._verify = False
        # self._ret_data = {}  # DottableDict()
        # self._ret_data.allowDotting()
        self._rep_num = 3
        self._rep_sleep = 1

    # @property
    # def ret_data(self):
    #     return self._ret_data

    # @ret_data.getter
    # def ret_data(self):
    #     return self._ret_data

    @property
    def verify(self):
        return self._verify

    @verify.setter
    def verify(self, value):
        if type(value) == bool:
            self._verify = value
        else:
            self._verify = False

    @verify.getter
    def verify(self):
        return self._verify

    @property
    def headers(self):
        return self._header

    @headers.setter
    def headers(self, value):
        if verify_json(value) is True:
            self._header = value
        else:
            raise Exception(
                f"header not json , header value now :{self._header}")

    @headers.getter
    def headers(self):
        return self._header

    @property
    def cookie(self):
        return self._cookie

    @cookie.setter
    def cookie(self, value):
        try:
            value["name"]
            value["value"]
        except Exception as e:
            raise e

        try:
            value["domain"]
        except Exception:
            value["domain"] = ""
        try:
            value["path"]
        except Exception:
            value["path"] = "/"
        self._cookie.set(value["name"], value["value"],
                         value["domain"], value["path"])

    @cookie.getter
    def cookie(self):
        return self._cookie

    @property
    def timeout(self):
        return self._timeout

    @timeout.setter
    def timeout(self, value):
        if type(value) != int:
            try:
                value = int(value)
            except Exception as e:
                raise e

        self._timeout = value

    @timeout.getter
    def timeout(self):
        return self._timeout

    @property
    def rep_num(self):
        return self._rep_num

    @rep_num.setter
    def rep_num(self, value):
        if type(value) == int:
            self._rep_num = value
        else:
            try:
                self._rep_num = int(self._rep_num)
            except ValueError:
                self._rep_num = 3

    @rep_num.getter
    def rep_num(self):
        return self._rep_num

    @property
    def rep_sleep(self):
        return self._rep_sleep

    @rep_sleep.setter
    def rep_sleep(self, value):
        if type(value) == int:
            self._rep_sleep = value
        else:
            try:
                self._rep_sleep = int(self._rep_sleep)
            except ValueError:
                self._rep_sleep = 1

    @rep_sleep.getter
    def rep_sleep(self):
        return self._rep_sleep

    def req(self, req_type="POST", url="", body=None, json_data=None, params_data=None, files_data=None):
        if self._header == {}:
            return {
                "code": 500,
                "success": False,
                "msg": "header头没有指定",
                "data": {}
            }
        if validators.url(url) is not True:
            return {
                "code": 500,
                "success": False,
                "msg": "url没有指定",
                "data": {}
            }
        # self.session.timeout(self._timeout)

        if json_data is not None:
            if verify_json(json_data) is False:
                return {
                    "code": 500,
                    "success": False,
                    "msg": "参数错误",
                    "data": {}
                }
                #raise Exception(f"not json, json_data value now :{json_data}")
        resp = None

        for _ in range(self._rep_num):
            try:
                resp = self.session.request(
                    method=req_type.lower(),
                    url=url,
                    data=body,
                    json=json_data,
                    params=params_data,
                    files=files_data,
                    headers=self._header,
                    cookies=self._cookie,
                    timeout=self._timeout,
                )
                resp.encoding = "UTF-8"
                if resp.status_code in [200, 201, 202, 203, 204, 205, 206, 207, 300, 301, 302, 303, 304, 305, 306, 307]:
                    break
                time.sleep(self._rep_sleep)

            except Exception as e:
                return {
                    "code": 500,
                    "success": False,
                    "msg": f"连接错误: {e}",
                    "data": {}
                }

        try:
            json_data = resp.json()
        except Exception as e:
            print(e)
            json_data = {}

        # self._ret_data.code = resp.status_code
        # self._ret_data.json = json_data

        app_ret_json = {
            "code": resp.status_code,
            "success": json_data.get("success", False),
            "msg": json_data.get("msg", "请求失败"),
            "data": json_data,
        }

        return app_ret_json

    def __del__(self):
        try:
            if self.session is not None:
                self.session.close()
        except Exception as _:
            pass


HTTPS = HTTP


def https_get(url, params=None, headers={}):
    https = HTTPS()
    https.headers = headers
    res = https.req("get", url=url, params_data=params)
    del https
    res_class = DottableDict(res)
    res_class.allowDotting()
    return res_class


def https_post(url, json_data=None, headers={}):
    https = HTTPS()
    headers['accept'] = 'application/json'
    https.headers = headers
    https.timeout = 60
    res = https.req("post", url=url, json_data=json_data)
    del https
    res_class = DottableDict(res)
    res_class.allowDotting()
    return res_class


def https_file(url, files=None, headers={}):
    import requests
    #https = HTTPS()
    #https.headers = headers
    headers['Content-type'] = files.content_type
    res = requests.post(url, data=files, headers=headers, timeout=300)
    # res = https.req("post", url=url, json_data={}, files_data=files)
    res_data = {
        "code": res.status_code,
        "success": res.json()["success"],
        "msg": res.json()["msg"],
        "data": res.json()
    }
    del res
    res_class = DottableDict(res_data)
    res_class.allowDotting()
    return res_class
