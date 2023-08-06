#!/usr/bin/env python
#-*- coding:utf-8 -*-
import os 
from setuptools import setup, find_packages

MAJOR = 0
MINOR = 3
PATCH = 1
VERSION = f"{MAJOR}.{MINOR}.{PATCH}"

def get_install_requires():
    reqs = []
    return reqs
setup(
	name = "chailie",
	version = VERSION,
    author ="wangweidong",
    author_email = "17891967090@163.com",
    description='Due Diligence Toolkit Python project',
    long_description_content_type="text/markdown",
	url = 'https://alidocs.dingtalk.com/i/p/4oJRz0VRJyvmLZMydy0mV7WvjQn7MG89',
	long_description = open('README.md',encoding="utf-8").read(),
    python_requires=">=3.8",
    install_requires=get_install_requires(),

	packages = find_packages(),
 	# license = 'Apache',
   	classifiers = [
       'Programming Language :: Python',

    ],
    #包含的类型
    package_data={'': ['*.csv', '*.txt','.toml', "*.pyd",'*.exe', '*.db']}, #这个很重要
    include_package_data=True #也选上

)