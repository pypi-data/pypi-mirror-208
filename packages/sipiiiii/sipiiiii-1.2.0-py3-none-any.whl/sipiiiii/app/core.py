import os
import yaml
import json
import sys

from shutil import rmtree
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from .utils.config import fix
from .utils.Tools import get_current_path, read_app_yaml, is_encomm_char


class ExecAppClass(object):
    def __init__(self, file_path):
        self.file_path = file_path

    def run_python_app(self):
        cmd_line = input("请输出python解析器[python,python3或pypy](默认python):")
        if cmd_line is None or cmd_line == "":
            cmd_line = "python"
        # sys.path.append(self.cwd)
        # try:
        #     from app import app
        # except Exception as e:
        #     return False, f"错误: sipiiii项目路径. {e}"
        os.system(f"{cmd_line} {self.file_path}")
        # app.run(debug=True, port=port)
        return True, "服务器运行正常过，目前服务器已停止..."


class CreateAppTypeClass(object):
    def __init__(self, app_name, app_yaml, app_dir):
        self.app_name = app_name
        self.app_yaml = app_yaml
        self.app_dir = app_dir

    def __create_app_path(self):
        if os.path.exists(self.app_name):
            print(f"{self.app_name} 路径已存在，无法在不删除的情况下创建新项目.")
            is_rm = input("是否需要删除, 不删除则会退出程序(y/n)?")
            is_rm = is_rm.lower()
            if is_rm == "y":
                rmtree(self.app_name)
            elif is_rm == "n":
                return True, "退出"

        path = Path(f"{self.app_name}")
        path.mkdir(parents=True, exist_ok=True)

    def __create_code(self, code_type, app_type, code="", code_name="app"):
        if code_name != "app":
            status, msg = create_app_code(
                self.app_name, code_type, code, code_name)
            if not status:
                return False, f"创建代码出错, {msg}"
            return True, msg

        status, msg = create_framework_code(
            self.app_dir, self.app_name, self.app_yaml, code_type, app_type, code_name)
        if not status:
            return False, f"创建框架代码出错, {msg}"
        return True, msg

    def __create_python_requirements(self, app_type):
        requirements = input("输入导入的库(多个库用逗号分隔):")
        if requirements is None or requirements == "":
            requirements = ""

        if requirements.find(",") > -1:
            requirements = requirements.split(",")
        else:
            if requirements == "":
                requirements = []
            else:
                requirements = [requirements]

        if app_type == "fastapi":
            requirements.append('fastapi')
        if app_type == "flask":
            requirements.append('flask')
        if app_type == "openai":
            requirements.append('quart')
            requirements.append('quart_cors')
        if app_type == "streamlit":
            requirements.append('streamlit')

        status, requirements_file_path = create_requirements(requirements)
        if not status:
            return False, requirements_file_path

    def creaye_other_file(self, code_type):
        if code_type == "python":
            requirements_file = os.path.join(os.getcwd(), "requirements.txt")
            if not os.path.exists(requirements_file):
                self.__create_python_requirements("other")

        self.app_yaml = ""
        for path in os.listdir(os.getcwd()):
            if os.path.isfile(path):
                if path.find(".yaml") > -1:
                    openapi_file_path = os.path.join(os.getcwd(), path)
                    with open(openapi_file_path, "r", encoding="utf-8") as f:
                        openapi_yaml = f.read()
                    self.app_yaml = yaml.safe_load(openapi_yaml)
                    break

        if self.app_yaml == "":
            status, _, self.app_yaml, _ = yaml_app_info(None, "other")
            status, openapi_file_path = create_app_yaml(self.app_yaml)
            if not status:
                return False, openapi_file_path
        try:
            _ = self.app_yaml['info']['title']
        except Exception as e:
            return False, f"yaml 解析错误: {str(e)}"

        self.app_yaml['info']['title'] = self.app_name
        self.app_yaml['info']['description'] = self.app_name

        with open(openapi_file_path, "w", encoding="utf-8") as f:
            yaml.dump(self.app_yaml, stream=f, allow_unicode=True)

        return True, ""

    def create_streamlit_app(self, code_type):
        self.__create_app_path()
        if code_type == "python":
            self.__create_python_requirements("streamlit")

        status, openapi_file_path = create_app_yaml(self.app_yaml)
        if not status:
            return False, openapi_file_path

        code = f"""
import streamlit as st

def main():
    st.markdown("hello world!")

if __name__ == "__main__":
    st.set_page_config(
        page_title="{self.app_name}", page_icon=":pencil2:"
    )
    st.title("{self.app_name}")
    # st.sidebar.subheader("Configuration")
    main()
        """
        ststus, msg = self.__create_code(
            code_type, "streamlit", code=code, code_name="main")
        if not ststus:
            return False, msg

        ststus, msg = self.__create_code(code_type, "streamlit")
        if not ststus:
            return False, msg
        return True, f"创建streamlit框架代码成功, 项目目录: ./{self.app_name}"

    def create_flask_app(self, code_type):
        self.__create_app_path()

        if code_type == "python":
            self.__create_python_requirements("flask")

        status, openapi_file_path = create_app_yaml(self.app_yaml)
        if not status:
            return False, openapi_file_path

        ststus, msg = self.__create_code(code_type, "flask")
        if not ststus:
            return False, msg

        return True, f"创建flask框架代码成功, 项目目录: ./{self.app_name}"

    def create_fastapi_app(self, code_type):
        self.__create_app_path()

        if code_type == "python":
            self.__create_python_requirements("fastapi")

        status, openapi_file_path = create_app_yaml(self.app_yaml)
        if not status:
            return False, openapi_file_path

        ststus, msg = self.__create_code(code_type, "fastapi")
        if not ststus:
            return False, msg

        return True, f"创建fastapi框架代码成功, 项目目录: ./{self.app_name}"

    def create_openai_app(self, code_type):
        ai_plugin_json = {
            "schema_version": "",
            "name_for_human": "",
            "name_for_model": "",
            "description_for_human": "",
            "description_for_model": "",
            "auth": {
                "type": "none"
            },
            "api": {
                "type": "openapi",
                "url": "!HOSTNAME!/openapi.yaml",
                "is_user_authenticated": False
            },
            "logo_url": "!HOSTNAME!/logo.png",
            "contact_email": "support@example.com",
            "legal_info_url": "https://example.com/legal"
        }

        try:
            ai_plugin_json['schema_version'] = self.app_yaml.get(
                'info', {}).get('version')
            ai_plugin_json['name_for_human'] = self.app_yaml.get(
                'info', {}).get('title')
            ai_plugin_json['name_for_model'] = self.app_yaml.get(
                'info', {}).get('title')
            ai_plugin_json['description_for_human'] = self.app_yaml.get(
                'info', {}).get('description')
            ai_plugin_json['description_for_model'] = self.app_yaml.get(
                'info', {}).get('description')
        except Exception as e:
            return False, str(e)

        self.__create_app_path()

        if code_type == "python":
            self.__create_python_requirements("openai")

        status, openapi_file_path = create_app_yaml(self.app_yaml)
        if not status:
            return False, openapi_file_path

        status, plugin_json_file_path = create_app_config(
            self.app_name, ai_plugin_json, "openai")
        if not status:
            return False, plugin_json_file_path

        ststus, msg = self.__create_code(code_type, "openai")
        if not ststus:
            return False, msg

        return True, f"创建openai框架代码成功, 项目目录: ./{self.app_name}"


def get_app_name(app_name):
    if app_name is None:
        app_name = os.getcwd().lower()
        app_name = os.path.basename(app_name)
    if not is_encomm_char(app_name):
        return False, "应用名(当前目录)只能是纯英文"

    return True, app_name


def get_app_code_type(file_path):
    _fix = ""
    try:
        _fix = os.path.splitext(file_path)[-1].split(".")[-1]
    except Exception as e:
        return False, f"错误: {e}"

    if _fix not in fix.values():
        return False, f"{_fix} 不存在于 {list(fix.keys())}"

    new_fix = {v: k for k, v in fix.items()}
    return True, new_fix[_fix]


def yaml_app_info(yaml_file, app_type):
    openapi_yaml = None
    aiapi_dir = get_current_path()
    # if app_type != "openai":
    #     app_type = "other"
    if yaml_file is None:
        openapi_yaml = read_app_yaml(aiapi_dir, app_type)
    else:
        openapi_yaml = read_app_yaml(yaml_file, app_type)
    if openapi_yaml == "":
        return False, "没找到yaml文件.", None, None
    app_name = ""
    try:
        app_name = openapi_yaml['info']['title']
    except Exception as e:
        return False, str(e), None, None

    if app_name == "":
        return False, "yaml中没有找到 yaml[info][title]", None, None

    app_name = app_name.replace(" ", "")
    return True, app_name, openapi_yaml, aiapi_dir


def create_requirements(requirements):
    if type(requirements) != list:
        return False, "requirements 错误!"

    directory_path = os.getcwd()
    if not os.path.exists(directory_path):
        return False, f"{directory_path} 没有找到."

    requirements_file_path = os.path.join(directory_path, "requirements.txt")
    requirements_data = ""
    if len(requirements) > 0:
        requirements_data = "\n".join(requirements)

    with open(requirements_file_path, "w", encoding="utf8") as f:
        f.write(requirements_data)

    return True, requirements_file_path


def create_app_config(directory_path, plugin_json, app_type):
    if type(plugin_json) != dict:
        return False, "应用配置文件错误!"

    if not os.path.exists(directory_path):
        return False, f"{directory_path} 目录没有找到."

    # ai-plugin.json
    if app_type == "openai":
        app_type = "ai-plugin"
    else:
        app_type = "config"

    plugin_json_file_path = os.path.join(directory_path, f"{app_type}.json")
    # plugin_json_data = "\n".join(plugin_json_file_path)
    with open(plugin_json_file_path, encoding="utf-8", mode="w") as f:
        json.dump(plugin_json, f, indent=2)

    return True, plugin_json_file_path


def create_app_yaml(openapi_yaml):
    directory_path = os.getcwd()
    if not os.path.exists(directory_path):
        return False, f"{directory_path} 目录不存在"

    # openapi_yaml_file_path = os.path.join(directory_path, f"{app_type}.yaml")
    # if app_type is None:
    openapi_yaml_file_path = os.path.join(directory_path, "aiapi.yaml")
    # openapi.yaml
    # openapi_yaml_file_path = os.path.join(directory_path, f"{app_type}.yaml")

    # plugin_json_data = "\n".join(plugin_json_file_path)
    with open(openapi_yaml_file_path, encoding="utf-8", mode="w") as f:
        yaml.dump(openapi_yaml, stream=f, allow_unicode=True)

    return True, openapi_yaml_file_path


def create_app_code(app_path, code_type, code, code_name):
    _fix = fix.get(code_type, None)
    if _fix is None:
        return False, "没有获取到应用类型"

    app_file = os.path.join(app_path, f"{code_name}.{_fix}")
    with open(app_file, 'w', encoding="utf-8") as f:
        f.write(code)

    return True, "创建代码成功"


def create_framework_code(directory_path, app_path, openapi_yaml, code_type, app_type, code_name="app"):
    if openapi_yaml.get("paths", None) is None:
        openapi_yaml['paths'] = []
    env = Environment(loader=FileSystemLoader(f"{directory_path}"))
    # template.j2
    # if app_type != "openai":
    #     app_type = "other"
    j2_file = f"{code_type}_{app_type}"
    try:
        template = env.get_template(f'{j2_file}.j2')
        output = template.render(paths=openapi_yaml['paths'])
    except Exception as e:
        return False, str(e)
    _fix = fix.get(code_type, None)
    if _fix is None:
        return False, "没有获取到应用类型"
    # Write the output to a Python file
    app_file = os.path.join(app_path, f"{code_name}.{_fix}")
    with open(app_file, 'w', encoding="utf-8") as f:
        f.write(output)

    return True, "创建框架代码成功"
