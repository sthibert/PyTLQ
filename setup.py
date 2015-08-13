from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='pytlq',
    version='0.1',
    description='A Python package for solving Temporal Logic Queries',
    long_description=long_description,
    url='https://github.com/sthibert/pytlq',
    author='Simon Thibert',
    license='LGPL-2.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'pyparsing',
        'click',
    ],
    entry_points={
        'console_scripts': [
            'pytlq=pytlq.pytlq:cli',
        ],
    },
)
