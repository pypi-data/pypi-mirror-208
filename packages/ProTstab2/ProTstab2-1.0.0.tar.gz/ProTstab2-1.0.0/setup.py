# -*- coding: utf-8 -*-


from distutils.core import setup

from setuptools import find_packages

with open("README_EN.md", "r", encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='ProTstab2',  # 包名
    version='1.0.0',  # 版本号
    description='Protein prediction package',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Jianjun Zhao',
    author_email='20204227057@stu.suda.edu.cn',
    url='http://8.133.174.28:8989/DeepTP/',
    install_requires=[
        'rpy2==3.4.5',
        'scikit-learn==0.22.2',
        'tensorflow==2.4.0',
        'pandas==1.1.5',
        'lightgbm==2.3.1',
        'requests==2.24.0',
    ],
    license='MIT',
    packages=find_packages(),
    platforms=["all"],
    python_requires='>=3.6',
    classifiers=[
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        "License :: OSI Approved :: MIT License",
    ],
)
