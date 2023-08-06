# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tests', 'xeauth']

package_data = \
{'': ['*']}

install_requires = \
['appdirs>=1.4.4,<2.0.0',
 'click',
 'gnupg>=2.3.1,<3.0.0',
 'httpx>=0.19,<0.25',
 'param>=1.12.0,<2.0.0',
 'rich>=13.1.0,<14.0.0']

entry_points = \
{'console_scripts': ['xeauth = xeauth.cli:main'],
 'eve_panel.auth': ['XenonAuth = xeauth.integrations.eve_panel:XenonEveAuth'],
 'panel.auth': ['xeauth = xeauth.integrations.panel_server:XenonPanelAuth']}

setup_kwargs = {
    'name': 'xeauth',
    'version': '0.2.1',
    'description': 'Top-level package for xeauth.',
    'long_description': '======\nxeauth\n======\n\n\n.. image:: https://img.shields.io/pypi/v/xeauth.svg\n        :target: https://pypi.python.org/pypi/xeauth\n\n.. image:: https://img.shields.io/travis/jmosbacher/xeauth.svg\n        :target: https://travis-ci.com/jmosbacher/xeauth\n\n.. image:: https://readthedocs.org/projects/xeauth/badge/?version=latest\n        :target: https://xeauth.readthedocs.io/en/latest/?badge=latest\n        :alt: Documentation Status\n\n\n\n\nAuthentication client for the Xenon edark matter experiment.\n\n\n* Free software: MIT\n* Documentation: https://xeauth.readthedocs.io.\n\n\nFeatures\n--------\n\n* TODO\n\nCredits\n-------\n\nThis package was created with Cookiecutter_ and the `briggySmalls/cookiecutter-pypackage`_ project template.\n\n.. _Cookiecutter: https://github.com/audreyr/cookiecutter\n.. _`briggySmalls/cookiecutter-pypackage`: https://github.com/briggySmalls/cookiecutter-pypackage\n',
    'author': 'Yossi Mosbacher',
    'author_email': 'joe.mosbacher@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/jmosbacher/xeauth',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4',
}


setup(**setup_kwargs)
