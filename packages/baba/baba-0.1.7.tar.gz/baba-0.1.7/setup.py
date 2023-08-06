from setuptools import setup, find_packages

setup(
    name="baba",
    version="0.1.7",
    packages=find_packages(),
    author="jie.kim",
    author_email="ubbs@163.com",
    license='MIT',
    description="好爸爸的每个类都是被用来继承的。作为顶层设计，它为通用行为实现了最基础的标准实践。比如自动埋点、性能分析、任务流转、异常处理、单元测试等。",
    long_description=open('README.md',encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url="https://pypi.org/project/baba/",
)