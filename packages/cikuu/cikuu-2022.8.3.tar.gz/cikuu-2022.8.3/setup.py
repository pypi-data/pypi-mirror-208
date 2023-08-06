#!/usr/bin/env python
#-*- coding:utf-8 -*-
 
#############################################
# File Name: setup.py
# Author: cikuu
# Mail: info@cikuu.com
# Created Time: 2022-2-13
#############################################
 
from setuptools import setup, find_packages
 
setup(
  name = "cikuu",
  version = "2022.8.3",
  keywords = ("pip"),
  description = "cikuu tools",
  long_description = "add replace into soinit",
  license = "MIT Licence",
 
  url = "http://www.cikuu.com",
  author = "cikuu",
  author_email = "info@cikuu.com",
 
  packages = find_packages(),
  include_package_data = True,
  platforms = "any", #"pymysql","pika","fastapi","uvicorn","click==7.1.2", "fire","elasticsearch","marisa_trie",
  install_requires = ["requests"]  #>=2.27.1
)
