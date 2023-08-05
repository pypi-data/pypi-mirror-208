#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

import json
import os
import pathlib
from os.path import join as pjoin
from setuptools import setup, find_packages


from jupyter_packaging import (
    create_cmdclass,
    install_npm,
    ensure_targets,
    combine_commands,
    skip_if_exists
)

HERE = os.path.dirname(os.path.abspath(__file__))

# The name of the project
name = 'yfiles_jupyter_graphs'

# Representative files that should exist after a successful build
jstargets = [
    pjoin(HERE, 'yfiles_jupyter_graphs', 'nbextension', 'index.js'),
    pjoin(HERE, 'yfiles_jupyter_graphs', 'labextension', 'package.json'),
]

data_files_spec = [
    ('share/jupyter/nbextensions/yfiles-jupyter-graphs', 'yfiles_jupyter_graphs/nbextension', '**'),
    ('share/jupyter/labextensions/yfiles-jupyter-graphs', 'yfiles_jupyter_graphs/labextension', '**'),
    ('share/jupyter/labextensions/yfiles-jupyter-graphs', '.', 'install.json'),
    ('etc/jupyter/nbconfig/notebook.d', '.', 'yfiles-jupyter-graphs.json'),
]


cmdclass = create_cmdclass('jsdeps', data_files_spec=data_files_spec)
npm_install = combine_commands(
    install_npm(HERE, npm=['yarn'], build_cmd='build:prod'), ensure_targets(jstargets),
)
cmdclass['jsdeps'] = skip_if_exists(jstargets, npm_install)

# Get the package info from package.json
long_description = pathlib.Path(pjoin(HERE, 'README.md')).read_text()
pkg_json = json.loads(pathlib.Path(pjoin(HERE, 'package.json')).read_bytes())
version = (
    pkg_json['version']
    .replace('-alpha.', 'a')
    .replace('-beta.', 'b')
    .replace('-rc.', 'rc')
) 

setup_args = dict(
    name=name,
    version=version,
    url=pkg_json['homepage'],
    project_urls = {
        "License": "https://github.com/yWorks/yfiles-jupyter-graphs/blob/main/LICENSE.md",
        "Bug Tracker": "https://github.com/yWorks/yfiles-jupyter-graphs/issues",
        "Documentation": "https://yworks.github.io/yfiles-jupyter-graphs/"
    },
    author=pkg_json['author']['name'],
    author_email=pkg_json['author']['email'],
    description=pkg_json['description'],
    license='https://github.com/yWorks/yfiles-jupyter-graphs/blob/main/LICENSE.md',
    license_files=['LICENSE.md'],
    long_description=long_description,
    long_description_content_type='text/markdown',
    cmdclass=cmdclass,
    packages=find_packages(),
    install_requires=[
        'ipywidgets>=7.6.0'
    ],
    zip_safe=False,
    include_package_data=True,
    python_requires='>=3.6',
    platforms='Linux, Mac OS X, Windows',
    keywords=[
        'Jupyter', 
        'JupyterLab', 
        'JupyterLab3'
        'ipython',
        'widgets',
        'yfiles',
        'visualization',
        'graph',
        'diagrams'
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: IPython',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Multimedia :: Graphics',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Framework :: Jupyter',
        'Framework :: Jupyter :: JupyterLab',
        'Framework :: Jupyter :: JupyterLab :: 3',
        'Framework :: Jupyter :: JupyterLab :: Extensions',
        'Framework :: Jupyter :: JupyterLab :: Extensions :: Prebuilt',
    ],
)

setup(**setup_args)
