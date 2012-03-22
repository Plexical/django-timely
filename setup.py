#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='django-timely',
    description='Calendaring mixin for Django',
    packages=('timely',),
    author='Jacob Oscarson',
    author_email='jacob@plexical.com',
    url='https://github.com/Plexical/django-timely',
    licence='ISC',
    classifiers=(
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ),
)
