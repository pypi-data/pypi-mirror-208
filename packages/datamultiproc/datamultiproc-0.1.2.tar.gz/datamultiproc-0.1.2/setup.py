# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['datamultiproc']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0',
 'numpy>=1.24.3,<2.0.0',
 'pydantic-yaml>=0.11.2,<0.12.0',
 'pydantic>=1.10.7,<2.0.0']

setup_kwargs = {
    'name': 'datamultiproc',
    'version': '0.1.2',
    'description': 'A Python multiprocessing library for data processing with pipelines.',
    'long_description': "# datamultiproc: A Python multiprocessing data pipeline library\n\nCreate Processors, compose them into pipelines and process your data using Python's \nmultiprocessing library\n",
    'author': 'Magnus Glasder',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/mglasder/datamultiproc',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
