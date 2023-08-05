# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['lisf']
setup_kwargs = {
    'name': 'lisf',
    'version': '0.1.5',
    'description': 'Lazy Instantiated Singleton Factory',
    'long_description': 'None',
    'author': 'imi',
    'author_email': 'None',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'py_modules': modules,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
