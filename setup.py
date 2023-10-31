#!/usr/bin/env python3

from setuptools import setup

setup(
    name='ChIMES_Analysis',
    author='Qing WANG',
    author_email='qing.wang@outlook.fr',
    version='0.1.0',
    packages=['modules'],
    scripts=['bin/gen_frame'],
    classifiers=[
        'Programming Language :: Python',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'Operating System :: OS Independent',
        'Topic :: Scientific/Engineering'],
    keywords = ['ChIMES', 'Many-Body Potentials', 'Optimization'])
