# -*- coding: utf-8 -*-
import os
from setuptools import setup, find_packages
from kuto import __version__, __description__

try:
    long_description = open(os.path.join('kuto', "README.md"), encoding='utf-8').read()
except IOError:
    long_description = ""

setup(
    name="kuto",
    version=__version__,
    description=__description__,
    author="杨康",
    author_email="772840356@qq.com",
    url="https://gitee.com/bluepang2021/kuto",
    platforms="Android,IOS,Web,Api",
    packages=find_packages(),
    long_description=long_description,
    python_requires='>=3.9',
    classifiers=[
        "Programming Language :: Python :: 3.9"
    ],
    include_package_data=True,
    package_data={
        r'': ['*.yml'],
    },
    install_requires=[
        'requests-toolbelt==0.10.1',
        'jmespath==0.9.5',
        'jsonschema==4.17.0',
        'uiautomator2==2.16.13',
        'tidevice==0.6.1',
        'facebook-wda==1.4.6',
        'selenium==4.8.2',
        'webdriver-manager==3.5.2',
        'pytest==6.2.5',
        'pytest-rerunfailures==10.2',
        'pytest-ordering==0.6',
        'pytest-xdist==2.5.0',
        'pytest-dependency==0.5.1',
        'allure-pytest==2.9.45',
        'PyYAML==6.0',
        'pandas==1.3.4',
        'openpyxl==3.0.9',
        'XlsxWriter==3.0.2',
        'pycryptodome==3.14.1',
        'yagmail==0.15.293',
        'PyMySQL==0.10.1',
        'pymongo==4.0.1'
    ],
    extras_require={
        "ocr": ["easyocr==1.6.2"],
        "opencv": [
            'opencv-python==4.6.0.66',
            'opencv-contrib-python==4.6.0.66',
            'opencv-python-headless==3.4.18.65'
        ]
    },
    entry_points={
        'console_scripts': [
            'kuto = kuto.cli:main'
        ]
    },
)
