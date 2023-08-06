import requests
import yaml
import os
import shutil
from pathlib import Path


def get_outside_ip():
    ip = ""
    try:
        ip = requests.get("http://ifconfig.me/ip", timeout=5).text.strip()
    except Exception as e:
        pass
    return ip


def is_encomm_char(_str):
    if not _str.encode('UTF-8').isalpha():
        return False

    return True


def get_current_path():
    aiapi_dir = os.path.join(Path.home(), ".aiapi")
    if os.path.exists(aiapi_dir):
        return aiapi_dir
    else:
        path = Path(f"{aiapi_dir}")
        path.mkdir(parents=True, exist_ok=True)
        return aiapi_dir


def read_app_yaml(directory_path, app_type):
    openapi_yaml_file_path = directory_path
    if app_type is not None:
        if directory_path.find(".yaml") == -1:
            openapi_yaml_file_path = os.path.join(
                directory_path, f"template_{app_type}.yaml")
    try:
        with open(openapi_yaml_file_path, "r", encoding="utf-8") as f:
            openapi_yaml = f.read()
        openapi_yaml = yaml.safe_load(openapi_yaml)
    except Exception as e:
        print(e)
        return ""
    return openapi_yaml


def write_new_yaml(yaml_file, app_type):
    if app_type != "openai":
        return
    with open(yaml_file, "r", encoding="utf-8") as f:
        openapi_yaml = f.read()
    openapi_yaml = yaml.safe_load(openapi_yaml)
    openapi_yaml['openapi'] = "3.0.1"
    del openapi_yaml['swagger']
    with open(f"{os.getcwd()}{os.sep}aiapi.yaml", "w", encoding="utf") as f:
        yaml.dump(openapi_yaml, stream=f, allow_unicode=True)


def move_file(src_file, dst_file):
    try:
        shutil.move(src_file, dst_file)
    except FileNotFoundError:
        pass
    