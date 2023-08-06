#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""
import os
import re
from setuptools import setup, find_packages


with open(os.path.join('cellmaps_ppidownloader', '__init__.py')) as ver_file:
    for line in ver_file:
        if line.startswith('__version__'):
            version=re.sub("'", "", line[line.index("'"):])

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['cellmaps_utils',
                'fairscape-cli',
                'requests',
                'mygene',
                'tqdm']

setup_requirements = [ ]

test_requirements = ['requests_mock']

setup(
    author="Gege Qian",
    author_email='geqian@ucsd.edu',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    description="Downloads APMS edgelist data for CM4AI MuSIC pipeline",
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    long_description_content_type='text/x-rst',
    include_package_data=True,
    keywords='cellmaps_ppidownloader',
    name='cellmaps_ppidownloader',
    packages=find_packages(include=['cellmaps_ppidownloader']),
    package_dir={'cellmaps_ppidownloader': 'cellmaps_ppidownloader'},
    scripts=['cellmaps_ppidownloader/cellmaps_ppidownloadercmd.py'],
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/idekerlab/cellmaps_ppidownloader',
    version=version,
    zip_safe=False)
