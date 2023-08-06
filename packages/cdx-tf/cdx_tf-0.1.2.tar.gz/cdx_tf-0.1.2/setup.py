# -*- coding: utf-8 -*-

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cdx_tf", 
    version="0.1.2",  # will auto-update via pip_modify_setup.py
    author="Hans Buehler",
    author_email="github@buehler.london",
    description="Basic Python tools",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hansbuehler/cdx_tf",
    packages=setuptools.find_packages(),
    install_requires=[
         'numpy>=1.23', 'pandas>=1.5', 'scipy>=1.10', 'matplotlib>=3.7', 'sortedcontainers>=2.4', 'tensorflow>=2.11', 'psutil', 'cdxbasics>=0.2.40'
     ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
