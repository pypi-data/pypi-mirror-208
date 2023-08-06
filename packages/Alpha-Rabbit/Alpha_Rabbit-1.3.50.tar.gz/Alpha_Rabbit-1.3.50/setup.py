# -*-coding:utf-8 -*-

"""
1. del dist
2. python setup.py sdist bdist_wheel
3. twine upload dist/*
"""
from __future__ import print_function
from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="Alpha_Rabbit",
    version="1.3.50",
    author="lijiongting",
    author_email="448986334@qq.com",
    description="Alpha_Rabbit",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    url="",
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS',
        'Operating System :: Microsoft',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    python_requires='>=3.8',
    install_requires=[
        'statsmodels>=0.13.2',
        'numpy>=1.23.2',
        'pandas>=1.4.4',
    ],
    zip_safe=True,
)
