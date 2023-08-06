# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['spectrally_constrained_lvms']

package_data = \
{'': ['*']}

install_requires = \
['matplotlib>=3.5.2,<4.0.0',
 'numpy>=1.23.1,<2.0.0',
 'scikit-learn>=1.1.2,<2.0.0',
 'scipy>=1.8.1,<2.0.0',
 'sympy>=1.11.1,<2.0.0',
 'tqdm>=4.64.1,<5.0.0']

setup_kwargs = {
    'name': 'spectrally-constrained-lvms',
    'version': '0.1.0.2',
    'description': 'An optimisation implementation of linear transforms with a spectral constraint.',
    'long_description': '# Spectrally constrained LVMs\n\n![GitHub](https://img.shields.io/github/license/RyanBalshaw/spectrally-constrained-LVMs)\n![GitHub issues](https://img.shields.io/github/issues-raw/RyanBalshaw/spectrally-constrained-LVMs)\n![PyPI](https://img.shields.io/pypi/v/spectrally-constrained-lvms)\n![PyPI - Wheel](https://img.shields.io/pypi/wheel/spectrally-constrained-lvms?color=blueviolet)\n![Read the Docs](https://img.shields.io/readthedocs/spectrally-constrained-lvms)\n![GitHub last commit](https://img.shields.io/github/last-commit/RyanBalshaw/spectrally-constrained-LVMs)\n\nA repository for all code for the package. This is the first setup of this project.\n\nThe package can be installed using [pip](https://pypi.org/project/pip/):\n\n# Documentation\nPlease visit... for the documentation.\n\n## Purpose\nwords words words\n\n# Installation\n\n```sh\npip install package_name\n```\n\n*Current version:* 0.1.0\n\n# Requirements\n\nThis package used Python >= 3.xxx or later to run. For other python dependencies, please check the `pyproject.toml`\nfile included in this repository.\n\nNote that the following packages should be installed on your system:\n- Numpy\n\n# API usage\n\nA generic example is shown below:\n```shell\n\n```\n\n# Contributing\nWords words words\n\n# License\n',
    'author': 'Ryan Balshaw',
    'author_email': 'ryanbalshaw81@gmail.com',
    'maintainer': 'Ryan Balshaw',
    'maintainer_email': 'ryanbalshaw81@gmail.com',
    'url': 'https://github.com/RyanBalshaw/scICA',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
