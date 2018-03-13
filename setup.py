#!/usr/bin/env python

from setuptools import setup, find_packages
import os.path

setup(name='tap-purecloud',
      version='0.0.1',
      description='Singer.io tap for extracting data from the Genesys Purecloud API',
      author='Fishtown Analytics',
      url='http://fishtownanalytics.com',
      classifiers=['Programming Language :: Python :: 3 :: Only'],
      py_modules=['tap_purecloud'],
      install_requires=[
          'singer-python==5.0.12',
          'backoff==1.3.2',
          'requests==2.18.4',
          'python-dateutil==2.6.0',
          'PureCloudPlatformApiSdk==0.45.1.101',
          'PureCloudPlatformClientV2==26.0.0',
          'websockets==4.0.1'
      ],
      entry_points='''
          [console_scripts]
          tap-purecloud=tap_purecloud:main
      ''',
      packages=['tap_purecloud']
)
