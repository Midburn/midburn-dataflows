from setuptools import setup, find_packages
from os import path
from time import time

here = path.abspath(path.dirname(__file__))

if path.exists("VERSION.txt"):
    # this file can be written by CI tools (e.g. Travis)
    with open("VERSION.txt") as version_file:
        version = version_file.read().strip().strip("v")
else:
    version = str(time())

setup(
    name='midburn_dataflows',
    version=version,
    description='''Midburn Dataflows''',
    url='https://github.com/midburn/midburn-dataflows',
    author='''Midburn Tech''',
    license='MIT',
    packages=find_packages(exclude=['examples', 'tests', '.tox']),
    install_requires=['pyyaml', 'dataflows'],
)
