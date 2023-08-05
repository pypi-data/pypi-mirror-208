from setuptools import setup, find_packages

setup(
    name='nexus-utilities',
    version='0.3.0',
    author='James Larsen',
    author_email='james.larsen42@gmail.com',
    description='Common python utilities',
    long_description='This package is meant to hold various useful utilities for functionality I find myself using across multiple projects.  I will try to keep this documentation updated as I expand the toolkit.',
    long_description_content_type='text/markdown',
    url='https://github.com/james-larsen/nexus-utilities',
    packages=['nexus_utils'],
    install_requires=[
        'boto3>=1.26.45',
        'configparser >=5.3.0',
        'sqlalchemy>=1.4.44',
        'keyring>=23.13.1',
        'chardet>=3.0.4',
        'twine>=3.4.0'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
)
