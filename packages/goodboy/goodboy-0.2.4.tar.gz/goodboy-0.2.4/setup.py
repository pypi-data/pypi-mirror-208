# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['goodboy', 'goodboy.types']

package_data = \
{'': ['*'],
 'goodboy': ['locale/*', 'locale/en/LC_MESSAGES/*', 'locale/ru/LC_MESSAGES/*']}

extras_require = \
{':python_version >= "3.6" and python_version < "3.8"': ['typing-extensions>=4.0']}

setup_kwargs = {
    'name': 'goodboy',
    'version': '0.2.4',
    'description': 'Data validation tool',
    'long_description': '# Goodboy: Data Validation for Python\n\nThis project is currently in an early stage of development.',
    'author': 'Maxim Andryunin',
    'author_email': 'maxim.andryunin@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
