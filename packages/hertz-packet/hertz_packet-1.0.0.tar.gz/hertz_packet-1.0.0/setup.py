# -*- coding: utf-8 -*-


from distutils.core import setup

from setuptools import find_packages

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name='hertz_packet',  # 包名
    version='1.0.0',  # 版本号
    description='release Hertz',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='luke9012',
    author_email='luke781520097@163.com',
    url='https://github.com/luke1879012/hertz_packet',
    install_requires=[
        'requests~=2.27.1',
    ],
    license='MIT',
    packages=find_packages(),
    platforms=["all"],
    python_requires='>=3.6',
    classifiers=[
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Natural Language :: Chinese (Simplified)',
        'Programming Language :: Python :: 3',
        "License :: OSI Approved :: MIT License",
    ],
)
