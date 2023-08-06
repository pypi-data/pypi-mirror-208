# -*- coding: UTF-8 -*-

from setuptools import setup

setup(
    name='log_check',
    version='2.4.0',
    description='LOG 检查工具',
    author='ice_summer',
    license='MIT',
    zip_safe=False,
    py_modules=['log_check'],
    url='https://gitlab.gz.cvte.cn/i_guozhihou/log_check',
    author_email='2053620282@qq.com',
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
    entry_points={'console_scripts': [
        'logc = log_check:main',
    ]},
)
