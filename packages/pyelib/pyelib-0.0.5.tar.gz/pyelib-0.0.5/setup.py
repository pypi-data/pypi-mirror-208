from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '0.0.5'

PACKAGE_NAME = "pyelib"
DESCRIPTION = 'pyelib是一个Python库，为标准库和第三方库提供易于使用的函数封装。'
LONG_DESCRIPTION = 'pyelib是一个Python库，为标准库和第三方库提供易于使用的函数封装。'
AUTHOR_NAME = "Xuehang Cang"
AUTHOR_EMAIL = "xuehangcang@outlook.com"
PROJECT_URL = "https://github.com/xuehangcang/pyelib"
REQUIRED_PACKAGES = ["pymongo", "openai"]  # 第三方工具
PROJECT_KEYWORDS = ["pymongo"]  # 关键字

# 阅读更多关于分类器的信息  https://pypi.org/classifiers/
CLASSIFIERS = [
    "Programming Language :: Python :: 3",
    "Operating System :: Unix",
    "Operating System :: MacOS :: MacOS X",
    "Operating System :: Microsoft :: Windows"]

setup(
    name=PACKAGE_NAME,
    version=VERSION,
    author=AUTHOR_NAME,
    author_email=AUTHOR_EMAIL,
    description=DESCRIPTION,
    url=PROJECT_URL,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=REQUIRED_PACKAGES,
    keywords=PROJECT_KEYWORDS,
    classifiers=CLASSIFIERS
)
