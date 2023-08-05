# encoding:utf-8
from setuptools import find_packages
from setuptools import setup

from pkg.version import __version__

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="lesscode_tool",
    version=__version__,
    description="低代码生成工具",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="navysummer",
    author_email="navysummer@yeah.net",
    packages=find_packages(),
    url="https://gitee.com/navysummer/lesscodeTool",
    platforms="any",
    include_package_data=True,
    # include_dirs=["pkg/lesscode"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        # "SQLAlchemy~=2.0.12",
        "click~=8.1.3"],
    entry_points={"console_scripts": ['lesscodeTool = pkg.lesscode_tool:main']}
)

"""
# 先升级打包工具
pip install --upgrade setuptools wheel twine

# 打包
python setup.py sdist bdist_wheel

# 检查
twine check dist/*

# 上传pypi
twine upload dist/*
twine upload dist/* --repository-url https://pypi.chanyeos.com/ -u admin -p shangqi
# 安装最新的版本测试
pip install -U lesscode_tool -i https://pypi.org/simple
pip install -U lesscode_tool -i https://pypi.chanyeos.com/simple

"""
