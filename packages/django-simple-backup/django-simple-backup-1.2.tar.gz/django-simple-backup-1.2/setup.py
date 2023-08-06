import ez_setup
ez_setup.use_setuptools()
from distutils.core import setup
from setuptools import find_packages

with open('README.rst', 'r') as f:
    long_description = f.read()

setup(
    name='django-simple-backup',
    version     = '1.2',
    author        = 'Evgeny Fadeev',
    author_email = 'evgeny.fadeev@gmail.com',
    url            = '',
    description    = 'A simple backup command for Django',
    packages=find_packages(),
    python_requires='<3',
    include_package_data=True,
    long_description=long_description,
)

