# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['folioclient']

package_data = \
{'': ['*']}

install_requires = \
['httpx>=0.23.3,<0.24.0', 'pyyaml>=6.0,<7.0']

setup_kwargs = {
    'name': 'folioclient',
    'version': '0.50.0',
    'description': 'An API wrapper over the FOLIO LSP API Suite OKAPI.',
    'long_description': '# FolioClient\n![example workflow](https://github.com/fontanka16/FolioClient/actions/workflows/python-package.yml/badge.svg)    \nFOLIO Client is a simple python (3) wrapper over the FOLIO LMS system API:s\nTest\n\n## Features\n* Convenient FOLIO login and OKAPI Token creation\n* Wrappers for various REST operations\n* Most common reference data for inventory are retrieved as cached properties. \n* Fetches the latest released schemas for instances, holdings and items. Very useful for JSON Schema based validation.\n\n## Installing\n```pip install folioclient ```\n',
    'author': 'Theodor Tolstoy',
    'author_email': 'github.teddes@tolstoy.se',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/FOLIO-FSE/folioclient',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
