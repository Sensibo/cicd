#!/usr/bin/env python3
import os

from setuptools import setup, find_packages

setup(
    name='cicd',
    version='1.0.0',
    description='CICD tools for sensibo',
    author='Shlomp',
    author_email='shlomimatichin@gmail.com',
    url='https://github.com/Sensibo/cicd',
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    include_package_data=True,
    install_requires=[
        'urllib3',
        'argcomplete',
        'boto3',
        'requests',
        'slackclient==1.3.1',
    ],
    entry_points={
        'console_scripts': [
            'cicd=cicd.main:entry_point',
        ],
    },
)
