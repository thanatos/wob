#!/usr/bin/env python

from distutils.core import setup

setup(
    name='Wob',
    version='0.1',
    description='Python web framework',
    author='Roy Wellington Ⅳ',
    packages=['wob', 'wob.http', 'wob.routing'],
)
