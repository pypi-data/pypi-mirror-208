# -*- coding=utf-8 -*- 
# github: night_handsomer
# csdn: 惜年_night
# mirror: https://pypi.tuna.tsinghua.edu.cn/simple/


import setuptools

with open("README.md", "r", encoding="utf8") as f:
    long_description = f.read()

setuptools.setup(
    name="baseToImgX",
    version="1.0",
    author="xinian_night",
    author_email="1912681536@qq.com",
    description="略略略",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",

    ],
    install_requires=[

    ],
    python_requires=">=3",
)
