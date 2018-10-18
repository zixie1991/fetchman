#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

packages=['fetchman']

with open('requirements.txt') as f:
    required = f.read().splitlines()


setup(
    name='fetchman',
    version='0.1.0',
    description='a light weight web crawler',
    author='zixie1991',
    author_email='zixie1991@163.com',
    url='',
    packages=packages,
    include_package_data=True,
    install_requires=required,
    license='MIT',
    zip_safe=False,
)
