#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

requirements = ['mne', 'pandas', 'matplotlib', 'numpy', 'pysimplegui', 'Pillow', 'pyyaml', 'multimethod']

setup(
    author="neurotechnology",
    author_email='support@neurotechnology.com',
    python_requires='>=3.8',
    classifiers=[
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    description="BrainAccess Python API",
    install_requires=requirements,
    long_description='BrainAccess Python API',
    include_package_data=True,
    keywords='brainaccess',
    name='brainaccess',
    packages=find_packages(include=['brainaccess', 'brainaccess.*']),
    url='https://www.neurotechnology.com/brainaccess.html',
    version='2.3.0',
    zip_safe=False,
)
