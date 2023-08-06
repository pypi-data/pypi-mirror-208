# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['authcli', 'authcli.management.commands', 'authcli.migrations']

package_data = \
{'': ['*']}

install_requires = \
['Django>=4,<5']

setup_kwargs = {
    'name': 'django-auth-cli-certic',
    'version': '0.1.2',
    'description': 'Outils CLI pour gestion des utilisateurs dans Django',
    'long_description': None,
    'author': 'Mickaël Desfrênes',
    'author_email': 'mickael.desfrenes@unicaen.fr',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3,<4',
}


setup(**setup_kwargs)
