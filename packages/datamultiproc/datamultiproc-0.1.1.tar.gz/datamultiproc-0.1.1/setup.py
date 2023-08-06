# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['datamultiproc']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'datamultiproc',
    'version': '0.1.1',
    'description': '',
    'long_description': "# datamultiproc: A Python multiprocessing data pipeline library\n\nCreate Processors, compose them into pipelines and process your data using Python's \nmultiprocessing library\n",
    'author': 'Magnus Glasder',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/mglasder/datamultiproc',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
