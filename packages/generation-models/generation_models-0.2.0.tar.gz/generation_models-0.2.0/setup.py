# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['generation_models']
install_requires = \
['pydantic>=1.5.1,<2.0.0']

setup_kwargs = {
    'name': 'generation-models',
    'version': '0.2.0',
    'description': 'generation API data model',
    'long_description': 'None',
    'author': 'battery_al',
    'author_email': 'allenlawrence94@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'py_modules': modules,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
