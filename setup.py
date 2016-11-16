#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

with open('README.md') as readme_file:
    readme = readme_file.read()

with open('HISTORY.md') as history_file:
    history = history_file.read()

requirements = [
    "logging",
    "argparse",
    "numpy",
    "matplotlib",
    "pandas",
    "more_itertools",
    "seaborn"
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='cdgo',
    version='0.1.0a0',
    description=("A Framework for Analysing Circular Dichroism Spectroscopy "
                 "Data Using CDPro"),
    long_description=readme + '\n\n' + history,
    author="Shane Eric Gordon",
    author_email='segordon.public@gmail.com',
    url='https://github.com/s-gordon/cdgo',
    packages=[
        'cdgo',
    ],
    package_dir={'cdgo': 'cdgo'},
    entry_points={
        'console_scripts': [
            'cdgo = cdgo.__main__:main'
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='cdgo',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    # test_suite='tests',
    # tests_require=test_requirements
)
