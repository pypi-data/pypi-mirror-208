import os
import multiprocessing
import prettytable as pt
import sys
import time
import yaml

from requests_toolbelt.multipart.encoder import MultipartEncoder
from pathlib import Path

from .core import CreateAppTypeClass, yaml_app_info, ExecAppClass, get_app_code_type, get_app_name

from .utils.ZipFileTool import zip_folder
from .utils.HttpSDK import https_get, https_post, https_file
from .utils.Tools import get_outside_ip, is_encomm_char, write_new_yaml, move_file
from .utils.config import app_all_types, server_host, fix


def process_update_outside_ip(domain, _token):
    while True:
        try:
            time.sleep(60 * 30)
        except KeyboardInterrupt:
            break

        outside_ip = get_outside_ip()
        headers = {
            "Content-type": "application/json",
            "authorization": _token
        }
        url = f"{server_host}/system/openapi/modify/domain/bind/ip"
        data = {
            "domain": domain,
            "ip": outside_ip
        }
        response = https_post(url, json_data=data, headers=headers)
        if not response.success:
            print(f"更新域名错误: {response.msg}")
        else:
            print(f"域名IP已更新: {domain} -> {outside_ip}")


def get_token():
    _token = ""
    home_dir_file = os.path.join(Path.home(), ".sipitoken")
    if os.path.exists(home_dir_file):
        with open(home_dir_file, 'r', encoding='utf8') as f:
            _token = f.read()
    if _token == "":
        return False, "请登录 sipiiiii, 使用 sipiiiii -L 进行登录, 使用 sipiiiii -h 获得帮助"

    return True, _token


# 创建项目
def create_app_project():
    status, _token = get_token()
    if not status:
        return False, _token, ""

    print("""
    *** 应用名称必须英文
    *** 可以使用向导模式创建应用和使用模版创建应用
        """)

    while True:
        is_wizard_create = input("y使用向导创建应用,n使用模版生成(y/n):")
        is_wizard_create = is_wizard_create.lower()

        if is_wizard_create == "y":
            app_name = input("请输入应用名:")
            if app_name == "" or not is_encomm_char(app_name):
                print("应用名不能为空, 并且应用名只能使用英文字母")
                continue

            app_desc = input("请输入应用说明:")
            app_version = input("请输入应用版本(默认 v1.0):")
            if app_version == "":
                app_version = "v1.0"
            print(f"应用名: {app_name}, 应用说明: {app_desc}, 应用版本: {app_version}")

            status, yaml_data = create_yaml(
                app_name, app_version, app_desc)
            if not status:
                print(yaml_data)
                continue

            with open(f"{os.getcwd()}{os.sep}aiapi.yaml", "w", encoding="utf-8") as f:
                f.write(yaml_data)

            status, msg, app_name, app_type = create_app(
                f"{os.getcwd()}{os.sep}aiapi.yaml")
            if status:
                write_new_yaml(
                    f"{os.getcwd()}{os.sep}aiapi.yaml", app_type)

            # os.remove(f"{os.getcwd()}{os.sep}aiapi.yaml")
            break

        elif is_wizard_create == "n":
            status, msg, app_name, _ = create_app(None)
            break
        else:
            continue

    move_file(f"{os.getcwd()}{os.sep}requirements.txt",
              f"{os.getcwd()}{os.sep}{app_name}{os.sep}requirements.txt")

    move_file(f"{os.getcwd()}{os.sep}aiapi.yaml",
              f"{os.getcwd()}{os.sep}{app_name}{os.sep}aiapi.yaml")
    return status, msg, app_name


# 创建yaml模版
def create_yaml(app_name, app_version, app_desc):
    status, _token = get_token()
    if not status:
        return False, _token

    while True:
        route_num = input("请输入有多少个接口(默认无接口):")
        if route_num == "":
            route_num = 0

        try:
            route_num = int(route_num)
            break
        except Exception as _:
            print("接口数量必须为数字")

    route_json = {
        "swagger": "2.0",
        "info": {
            "title": app_name,
            "description": app_desc,
            "version": app_version
        },
        "paths": {}
    }
    for i in range(route_num):
        i = i + 1
        api_method = input(f"第{i}个接口的请求方式(get, post, put, delete):")
        api_name = input(f"第{i}个接口的名字,请用英文:")
        api_dec = input(f"第{i}个接口的描述:")
        parameters_end = False
        params_list = []
        while parameters_end:
            params_name = input("请输入参数名:")
            params_type = input("请输入参数类型(float, int, string):")
            params_list.append({
                "name": params_name,
                "in": "query",
                "schema": {
                    "type": params_type
                }
            })
            parameters_end = input("是否继续录入参数(y/n):")
            parameters_end = parameters_end.lower()
            if parameters_end == "y":
                parameters_end = True
            else:
                parameters_end = False
        route_json['paths'][f"/{api_name}"] = {
            api_method: {
                "summary": api_dec,
                # "parameters": params_list,
                "responses": {
                    "200": "OK"
                }
            }
        }
    yaml_data = yaml.dump(route_json, allow_unicode=True)

    return True, yaml_data

# 通过yaml直接创建APP


def create_app(yaml_file=None):
    if yaml_file is not None and yaml_file.find(".yaml") == -1:
        return False, "参数错误, 参数并不是Yaml文件, 请查看 sipiiiii -h", "", ""
    status, _token = get_token()
    if not status:
        return False, _token, "", ""

    while True:
        code_type = input(
            f"请输入创建编程语言{list(fix.keys())}(默认第一个): "
        )

        if code_type == "":
            code_type = list(fix.keys())[0]

        _code_type = app_all_types.get(code_type, None)
        if _code_type is None:
            print(f"编程语言的范围为: {list(fix.keys())}")
            continue
        break

    while True:
        app_type = input(
            f"请创建应用程序类型{app_all_types[code_type]}(默认第一个): "
        )
        if app_type == "":
            app_type = app_all_types[code_type][0]
        if app_type not in app_all_types[code_type]:
            print(f"应用程序类型的范围为: {app_all_types[code_type]}")
            continue
        break

    status, app_name, app_yaml, app_dir = yaml_app_info(yaml_file, app_type)
    if not status:
        return False, f"创建应用失败: {app_name}", "", ""

    catc = CreateAppTypeClass(app_name, app_yaml, app_dir)
    method_of_catc = getattr(catc, f"create_{app_type}_app")
    status, msg = method_of_catc(code_type)
    return status, msg, app_name, app_type


def dev_app():
    print("测试运行....\r\n")
    run_main = input("请输入APP运行文件:")
    cwd = os.getcwd()

    file_path = os.path.join(cwd, run_main)
    file_path = Path(f'{file_path}')
    if not file_path.exists():
        return False, "错误: 不存在项目路径, 请到项目路径下运行"

    status, code_type = get_app_code_type(file_path)
    if not status:
        return False, code_type

    eac = ExecAppClass(file_path)

    method_of_catc = getattr(eac, f"run_{code_type}_app")
    status, msg = method_of_catc()

    return status, msg


def localdepl(app_name):
    status, _token = get_token()
    if not status:
        return False, _token

    status, app_name = get_app_name(app_name)
    if not status:
        return False, f"获取应用名错误: {app_name}"

    app_cn_name = input("请输入应用别名:")
    if app_cn_name == "":
        app_cn_name = app_name

    # description = input("请输入应用说明:")

    print(f"本地部署: {app_name} 项目\r\n")

    outside_ip = get_outside_ip()
    if outside_ip == "":
        return False, "无法访问互联网"

    print(f"本机外网IP: {outside_ip}")
    status, _token = get_token()
    if not status:
        return False, _token

    run_main = input("请输入APP运行文件:")

    if run_main.find(".") == 0:
        return False, "APP运行文件必须是文件名加文件后缀"

    run_main_fix = run_main.split(".")
    if len(run_main_fix) != 2:
        return False, "APP运行文件输入不合法"

    if run_main_fix[-1] not in list(fix.values()):
        return False, f"APP运行文件不在允许的列表范围内: {list(fix.keys())}"

    cwd = os.getcwd()
    file_path = os.path.join(cwd, run_main)
    file_path = Path(f'{file_path}')
    if not file_path.exists():
        return False, "错误: 不存在项目路径, 请到项目路径下运行"

    app_language = [k for k, v in fix.items() if v == run_main_fix[-1]][0]

    url = f"{server_host}/system/openapi/app/local/deployment"
    headers = {
        "Content-type": "application/json",
        "authorization": _token
    }
    data = {
        "app_name": app_name,
        "app_dock": "app",
        "app_cn_name": app_cn_name,
        "ip": outside_ip,
        "description": f"本地部署的{app_name}",
        "app_language": app_language
    }

    response = https_post(url, json_data=data, headers=headers)
    if response.code != 200:
        return False, "内部服务器错误，请稍后再试"

    if not response.success:
        return False, response.msg

    print(f"域名: {response.data['domain']}")
    time.sleep(3)
    p = multiprocessing.Process(
        target=process_update_outside_ip, args=(response.data['domain'], _token), daemon=True)
    p.start()

    status, code_type = get_app_code_type(file_path)
    if not status:
        return False, code_type

    eac = ExecAppClass(file_path)

    method_of_catc = getattr(eac, f"run_{code_type}_app")
    status, msg = method_of_catc()

    return status, msg


def stop_app(app_name=None):
    status, _token = get_token()
    if not status:
        return False, _token

    status, app_name = get_app_name(app_name)
    if not status:
        return False, f"获取应用名错误: {app_name}"

    data = {"app_name": app_name}

    headers = {
        "Content-type": "application/json",
        "authorization": _token
    }
    url = f"{server_host}/system/openapi/app/stop"
    response = https_post(url, json_data=data, headers=headers)
    if not response.success:
        return False, response.msg

    return True, response.msg


def deployed():
    status, _token = get_token()
    if not status:
        return False, _token
    print("""
    *** 必须在项目目录下进行操作
    *** 如果是对外服务暴露的端口必须为8000
    *** 之前部署过的项目再部署则是更新, 域名不会改变
    """)
    headers = {
        "Content-type": "application/json",
        "authorization": _token
    }

    url = f"{server_host}/system/openapi/users/check/token"
    # response = requests.get(url,headers=headers, timeout=20)
    response = https_get(url, headers=headers)

    if not response.success:
        return False, "用户令牌无效，请登录使用 sipiiiiii -L 登录."

    if not response.data["exist"]:
        return False, "用户令牌无效或超时，请登录使用 sipiiiiii -L 登录."

    status, app_name = get_app_name(None)
    if not status:
        return False, f"获取应用名错误: {app_name}"

    app_cn_name = input("请输入APP别名:")
    # input("please input APP docking party(chatgpt, other):")
    app_dock = "other"
    run_main = input("请输入APP运行文件:")

    if app_cn_name == "" or run_main == "":
        return False, "APP别名 或者 APP运行文件的不能为空."

    if run_main.find(".") == 0:
        return False, "APP运行文件必须是文件名加文件后缀"

    run_main_fix = run_main.split(".")
    if len(run_main_fix) != 2:
        return False, "APP运行文件输入不合法"

    cwd = os.getcwd()
    file_path = os.path.join(cwd, run_main)
    file_path = Path(f'{file_path}')
    if not file_path.exists():
        return False, "错误: 不存在项目路径, 请到项目路径下运行, 或者使用sipiiiii -n 创建项目"

    if run_main_fix[-1] not in list(fix.values()):
        return False, f"APP运行文件不在允许的列表范围内: {list(fix.keys())}"

    app_language = [k for k, v in fix.items() if v == run_main_fix[-1]][0]

    catc = CreateAppTypeClass(app_name, "", "")
    status, msg = catc.creaye_other_file(app_language)

    if not status:
        return False, msg

    zip_file_path = zip_folder(cwd)
    if zip_file_path is None:
        return False, "应用程序打包失败。请检查应用程序目录中是否存在异常文件或文件夹"

    print(f"远程部署: {app_name} 项目\r\n")
    filename = os.path.basename(cwd)
    files = MultipartEncoder(fields={
        'file': (f"{app_name}.zip", open(zip_file_path, 'rb'), 'application/octet-stream'),
    })

    url = f"{server_host}/system/openapi/app/upload"
    response = https_file(url, files=files, headers=headers)

    if response['code'] != 200:
        return False, "内部服务器错误，请稍后再试"

    if not response['success']:
        return False, response['msg']

    url = f"{server_host}/system/openapi/app/deployment"
    data = {
        "file_uuid": response['data']['file_uuid'],
        "app_cn_name": app_cn_name,
        "app_language": app_language,
        "app_dock": app_dock,
        "run_main": run_main
    }
    headers['Content-type'] = "application/json"
    # headers['accept'] = 'application/json'

    response = https_post(url, json_data=data, headers=headers)
    # response = requests.post(url, data=files, headers=headers, timeout=300)
    # print(response)
    if response.code != 200:
        return False, "内部服务器错误，请稍后再试"

    if not response.success:
        return False, response.msg

    # return True, "ok"

    # status, info_json, _ = get_app_info(filename)
    # if not status:
    #     return False, "部署成功，状态获取失败"

    # bar = ProgPercent(50, monitor=True)
    print("正在远程部署...\r\n")
    i = 0
    while True:
        if i >= 60 * 1:
            break
        i += 1
        time.sleep(1)
        status, info_json, _ = get_app_info(filename.lower())
        if not status:
            continue

        if info_json['ServerStatus'] == "close" or info_json['ServerStatus'] == "exited":
            # bar.update(50)
            return True, f"\r\n应用程序部署出错，日志: \r\n{info_json['Log']}"

        if info_json['ServerStatus'] == "created" or info_json['ServerStatus'] == "running":
            # bar.update(50)
            return True, f"\r\n部署成功, \r\n域名: {info_json['Domain']}"

    # return True, response.data
    return False, "\r\n应用部署失败, 请检查应用是否可正常运行或者检查包是否正确"


def login(email, password):
    url = f"{server_host}/system/openapi/users/login"
    headers = {
        "Content-type": "application/json"
    }
    data = {
        "email": email,
        "password": password
    }
    # response = requests.post(url, json=data, headers=headers, timeout=20)
    response = https_post(url, json_data=data, headers=headers)
    if response.code != 200:
        return False, "服务器错误."
    if not response.success:
        return False, response.msg

    home_dir_file = os.path.join(Path.home(), ".sipitoken")
    with open(home_dir_file, 'w', encoding='utf-8') as f:
        f.write(response.data['token'])

    status, tally, info = get_tally()
    if status:
        return True, f"登录成功, 登录有效期3天, 剩余积分: {tally}, {info}"

    return False, "登录成功, 登录有效期3天, 获取积分失败."


def get_tally():
    status, _token = get_token()
    if not status:
        return False, _token

    url = f"{server_host}/system/openapi/users/tally"
    headers = {
        "Content-type": "application/json",
        "authorization": _token
    }
    response = https_get(url, headers=headers)
    # response = requests.get(url, headers=headers, timeout=20)
    if response.code != 200:
        return False, "服务器内部错误, 请稍后再试", ""

    if not response.success:
        return False, response.msg, ""

    tally = response.data['tally']
    tally = int(tally)
    info = f"可以部署{int(tally/20)}个远程应用或{int(tally/5)}个本地应用"
    return True, response.data['tally'], info


def restart_app(app_name):
    status, _token = get_token()
    if not status:
        return False, _token

    url = f"{server_host}/system/openapi/app/restart"
    headers = {
        "Content-type": "application/json",
        "authorization": _token
    }
    status, app_name = get_app_name(app_name)
    if not status:
        return False, f"获取应用名错误: {app_name}"

    response = https_post(
        url, json_data={"app_name": app_name}, headers=headers)
    if response.code != 200:
        return False, "服务器内部错误, 请稍后再试"

    if not response.success:
        return False, response.msg

    return True, response.msg


def get_app_info(app_name=None):
    status, _token = get_token()
    if not status:
        return False, {}, _token

    url = f"{server_host}/system/openapi/app/status"
    headers = {
        "Content-type": "application/json",
        "authorization": _token
    }
    status, app_name = get_app_name(app_name)
    if not status:
        return False, {}, f"获取应用名错误: {app_name}"
    app_name = app_name.lower()
    data = {"app_name": app_name}

    response = https_post(url, json_data=data, headers=headers)
    if response.code != 200:
        return False, {}, "服务器内部错误, 请稍后再试"

    if not response.success:
        return False, {}, response.msg

    app_info = response.data
    app_info = app_info['data']
    app_info_str = f"""
应用名称       : {app_info['AppName']}
应用别名       : {app_info['AppCnName']}
应用启动文件   : {app_info['AppRun']}
域名           : {app_info['Domain']}
应用状态       : {app_info['ServerStatus']}
创建时间       : {app_info['CreateTime']}
"""
    return True, app_info, app_info_str


def show_list():
    status, _token = get_token()
    if not status:
        return False, _token

    url = f"{server_host}/system/openapi/app/list"
    headers = {
        "Content-type": "application/json",
        "authorization": _token
    }

    #response = requests.get(url, headers=headers, timeout=20)
    response = https_get(url, headers=headers)
    if response.code != 200:
        return False, "服务器内部错误, 请稍后再试"

    if not response.success:
        return False, response.msg

    app_list = response.data['data']
    table = pt.PrettyTable(
        ['应用名', '应用别名', '域名', '应用状态', '创建时间'])
    for app in app_list:
        table.add_row((app['AppName'], app['AppCnName'], app['Domain'],
                      app['ServerStatus'], app['CreateTime']))

    return True, table


def get_cli_server_version():
    headers = {
        "Content-type": "application/json",
    }
    url = f"{server_host}/system/openapi/users/get/client"
    response = https_get(url, headers=headers)
    if response.code != 200:
        return False, "服务器内部错误, 请稍后再试"

    return response.msg


def update_template():
    pass


def activate_account():
    status, _token = get_token()
    if not status:
        return False, _token

    headers = {
        "Content-type": "application/json",
        "authorization": _token
    }

    url = f"{server_host}/system/openapi/users/verify/code"

    response = https_get(url, headers=headers)
    if response.code != 200:
        return False, "服务器内部错误, 请稍后再试"

    if not response.success:
        return False, f"获取验证码异常: {response.msg}"

    verify_code = ""
    while True:
        try:
            verify_code = input("请输出邮件中的 6位 验证码:")
            verify_code = int(verify_code)
        except KeyboardInterrupt:
            print("\r\n")
            sys.exit(1)
        except ValueError:
            print("验证码为纯6位数字")
            continue
        if verify_code == "":
            continue
        break

    url = f"{server_host}/system/openapi/users/verify/code"

    response = https_post(
        url, json_data={"code": verify_code}, headers=headers)
    if response.code != 200:
        return False, "服务器内部错误, 请稍后再试"

    if not response.success:
        return False, f"获取验证码异常: {response.msg}"

    return True, response.msg


def register(username, email, password):
    headers = {
        "Content-type": "application/json",
    }
    url = f"{server_host}/system/openapi/users/register"

    data = {
        "username": username,
        "password": password,
        "email": email
    }

    response = https_post(url, json_data=data, headers=headers)

    if response.code != 200:
        return False, "服务器内部错误, 请稍后再试"

    if not response.success:
        return False, f"注册异常: {response.msg}"

    print(f"用户: {username} 注册成功, 注册后需要接受邮件验证码并且输入验证码后才能使用")
    print("验证码也可以之后使用 -V 进行重新验证")

    home_dir_file = os.path.join(Path.home(), ".sipitoken")
    with open(home_dir_file, 'w', encoding='utf-8') as f:
        f.write(response.data['token'])

    headers["authorization"] = response.data['token']
    url = f"{server_host}/system/openapi/users/verify/code"

    response = https_get(url, headers=headers)
    if response.code != 200:
        return False, "服务器内部错误, 请稍后再试"

    if not response.success:
        return False, f"获取验证码异常: {response.msg}"

    ststus, msg = activate_account()

    return ststus, msg
