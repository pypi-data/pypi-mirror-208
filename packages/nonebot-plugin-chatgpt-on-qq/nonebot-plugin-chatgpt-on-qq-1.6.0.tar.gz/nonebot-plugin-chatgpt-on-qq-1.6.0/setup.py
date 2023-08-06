#!/usr/bin/env python
# coding:utf-8

from setuptools import find_packages, setup

setup(
    name='nonebot-plugin-chatgpt-on-qq',
    version='1.6.0',
    description='具有多对话功能的chatGPT聊天插件',
    long_description=open('README.rst').read(),
    author='颜曦',
    author_email='424504326@qq.com',
    maintainer='颜曦',
    maintainer_email='424504326@qq.com',
    packages=find_packages(),
    platforms=["all"],
    install_requires=[
        'nonebot-adapter-onebot>=2.2.1',
        'nonebot2>=2.0.0rc3',
        'openai>=0.27.0',
        'pydantic>=1.10.5',
        'regex>=2022.10.31',
        'aiohttp>=3.8.4'
    ],
    url='https://github.com/Suxmx/nonebot_plugin_chatgpt_turbo_on_qq',
    license='BSD License',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
    ],
)