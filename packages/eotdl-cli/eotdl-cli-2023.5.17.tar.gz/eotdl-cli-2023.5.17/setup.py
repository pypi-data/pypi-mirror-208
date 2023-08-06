# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['eotdl_cli',
 'eotdl_cli.commands',
 'eotdl_cli.src',
 'eotdl_cli.src.errors',
 'eotdl_cli.src.repos',
 'eotdl_cli.src.usecases',
 'eotdl_cli.src.usecases.auth',
 'eotdl_cli.src.usecases.datasets']

package_data = \
{'': ['*']}

install_requires = \
['pydantic>=1.10.6,<2.0.0',
 'pyjwt>=2.6.0,<3.0.0',
 'requests>=2.28.2,<3.0.0',
 'tqdm>=4.65.0,<5.0.0',
 'typer[all]>=0.7.0,<0.8.0']

entry_points = \
{'console_scripts': ['eotdl-cli = eotdl_cli.main:app']}

setup_kwargs = {
    'name': 'eotdl-cli',
    'version': '2023.5.17',
    'description': '',
    'long_description': '# eotdl-cli\n\nThis is the CLI for EOTDL.\n\n',
    'author': 'EarthPulse',
    'author_email': 'it@earthpulse.es',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
