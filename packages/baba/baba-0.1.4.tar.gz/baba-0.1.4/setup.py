from setuptools import setup, find_packages

setup(
    name="baba",
    version="0.1.4",
    packages=find_packages(),
    author="jie.kim",
    author_email="ubbs@163.com",
    license='MIT',
    description="好爸爸系列，追求朴素而踏实的实践。继承好爸爸的思想，轻松实现自动埋点、统计、错误处理、状态控制、任务流转、单元测试等功能",
    long_description=open('README.md',encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url="https://pypi.org/project/baba/",
)