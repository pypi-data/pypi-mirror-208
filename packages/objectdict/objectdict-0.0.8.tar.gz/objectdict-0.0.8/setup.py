# -*- coding: utf-8 -*-
# https://blog.konghy.cn/2018/04/29/setup-dot-py/
import shutil

import setuptools
import sys
import os

if sys.argv[-1] == 'publish':
    if os.system("pip freeze | grep twine"):
        print("twine not installed.\nUse `pip install twine`.\nExiting.")
        sys.exit()
    os.system("python setup.py sdist bdist_wheel")
    if os.system("twine check dist/*"):
        print("twine check failed. Packages might be outdated.")
        print("Try using `pip install -U twine wheel`.\nExiting.")
        sys.exit()
    os.system("twine upload dist/*")
    shutil.rmtree('dist')
    shutil.rmtree('build')

    sys.exit()

with open("README.md", "r") as fh:
    long_description = fh.read()

install_requires = [l.strip() for l in open('./requirements.txt').readlines() if l.strip()]
setuptools.setup(
        name="objectdict",  # 包的分发名称，使用字母、数字、_、-
        version="0.0.8",  # 版本号, 版本号规范：https://www.python.org/dev/peps/pep-0440/
        author="xzregg",  # 作者名字
        author_email="xzregg@gmail.com",  # 作者邮箱
        description="objectdict",  # 包的简介描述
        long_description=long_description,  # 包的详细介绍(一般通过加载README.md)
        long_description_content_type="text/markdown",  # 和上条命令配合使用，声明加载的是markdown文件
        url="https://github.com/xzregg/pyobjectdict",  # 项目开源地址，我这里写的是同性交友官网，大家可以写自己真实的开源网址
        py_modules=['objectdict'],
        # 如果项目由多个文件组成，我们可以使用find_packages()自动发现所有包和子包，而不是手动列出每个包，在这种情况下，包列表将是example_pkg
        classifiers=[  # 关于包的其他元数据(metadata)
                "Programming Language :: Python :: 2",  # 该软件包仅与Python3兼容
                "License :: OSI Approved :: MIT License",  # 根据MIT许可证开源
                "Operating System :: OS Independent",  # 与操作系统无关
        ],
        install_requires=install_requires,  # 依赖的包
        data_files=['requirements.txt'],
        python_requires='>=2.7'
)
