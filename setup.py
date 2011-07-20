#!/usr/bin/env python

from distutils.core import setup

setup(
    name='hyson',
    version='0.1dev',
    description='Ext JS integration utilities',
    author='Michail Sychev',
    author_email='m.sychev@axion-rti.ru',
    url='https://github.com/Axion/Hyson',
    license = 'GNU GPL3',
    packages = ['hyson', 'hyson.management', 'hyson.management.commands'],
    package_data={'hyson': ['docs/*', 'static/*']},
    requires = ['django (>=1.3)'],
)