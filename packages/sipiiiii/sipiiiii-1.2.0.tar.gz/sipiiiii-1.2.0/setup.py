
import setuptools
import sys
import os
from shutil import copyfile
from pathlib import Path

# from version import version
# from initsipiiiii import init_framework


def get_current_path():
    aiapi_dir = os.path.join(Path.home(), ".aiapi")
    if os.path.exists(aiapi_dir):
        return aiapi_dir
    else:
        path = Path(f"{aiapi_dir}")
        path.mkdir(parents=True, exist_ok=True)
        return aiapi_dir


def init_framework():
    aiapi_dir = get_current_path()

    # Replace 'template/template.yaml' with the path to the file you want to copy
    # src_file = f'sipiiiii{os.sep}template/template.yaml'
    # try:
    src_dir = os.path.join(os.getcwd(), "template")
    # src_dir = os.path.join('sipiiiii', "template")
    try:
        template_files = os.listdir(src_dir)
    except Exception as e:
        print(e)
        src_dir = os.path.join(os.getcwd(), "sipiiiii", "template")
        template_files = os.listdir(src_dir)

    for tFIle in template_files:
        src_file = os.path.join(src_dir, tFIle)

        # Use Path().resolve() to get the absolute path of the source file
        src_path = Path(src_file).resolve()

        # Use Path().joinpath() to get the destination path
        dest_path = Path(aiapi_dir).joinpath(tFIle)
        # Use Path().replace() to copy the file
        try:
            copyfile(src_path, dest_path)
        except Exception as e:
            print(str(e))
            continue

        # Check if the file was copied successfully
        if not dest_path.exists():
            continue

    return True, "初始化成功"


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

status, msg = init_framework()
if not status:
    print(msg)
    sys.exit(1)

setuptools.setup(
    # 包的分发名称，使用字母、数字、_、-
    name="sipiiiii",
    # 版本号, 版本号规范：https://www.python.org/dev/peps/pep-0440/
    version="1.2.0",
    # 作者名
    author="sipiiiii@admin",
    # 作者邮箱
    author_email="j0hn.wahahaha@gmail.com",
    # 包的简介描述
    description="depl sipiiiii, App Development Framework",
    # 包的详细介绍(一般通过加载README.md)
    long_description=long_description,
    # 和上条命令配合使用，声明加载的是markdown文件
    long_description_content_type="text/markdown",
    # 项目开源地址
    url="http://www.depl.run/",
    # 如果项目由多个文件组成，我们可以使用find_packages()自动发现所有包和子包，而不是手动列出每个包，在这种情况下，包列表将是example_pkg
    packages=setuptools.find_packages(),
    package_data={'template': ['*.j2', '*.yaml']},
    nclude_package_data=True,
    install_requires=[
        'httpx',
        'prettytable==3.7.0',
        'jinja2',
        'requests',
        'requests_toolbelt',
        'xmltodict',
        'validators',
        'pathlib',
        'jsonpath',
        'pyyaml'
    ],
    entry_points={
        'console_scripts': [
            'sipiiiii = sipiiiii.main:main'
        ]
    },
    # 关于包的其他元数据(metadata)
    classifiers=[
        # 该软件包仅与Python3兼容
        "Programming Language :: Python :: 3",
        # 根据MIT许可证开源
        "License :: OSI Approved :: MIT License",
        # 与操作系统无关
        "Operating System :: OS Independent",
    ],
)
