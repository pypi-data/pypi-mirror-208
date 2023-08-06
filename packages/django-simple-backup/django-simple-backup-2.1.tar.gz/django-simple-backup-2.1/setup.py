"""setup.py file for packaging django-simple-backup"""
from distutils.core import setup
from setuptools import find_packages

with open('README.rst', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='django-simple-backup',
    version     = '2.1',
    author        = 'Evgeny Fadeev',
    author_email = 'evgeny.fadeev@gmail.com',
    url            = '',
    description    = 'A simple backup command for Django',
    packages=find_packages(),
    python_requires='>2, <4',
    include_package_data=True,
    long_description=long_description,
    long_description_content_type="text/x-rst",
)
