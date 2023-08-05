# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['apicase',
 'apicase.assertion',
 'apicase.client',
 'apicase.common',
 'apicase.report',
 'apicase.report.html',
 'apicase.script']

package_data = \
{'': ['*']}

install_requires = \
['Jinja2>=3.1.2,<4.0.0',
 'PyYAML>=6.0,<7.0',
 'allure-pytest>=2.12.0,<3.0.0',
 'deepdiff>=6.3.0,<7.0.0',
 'jmespath>=1.0.1,<2.0.0',
 'loguru>=0.6.0,<0.7.0',
 'prettytable>=3.6.0,<4.0.0',
 'pydantic[dotenv]>=1.10.5,<2.0.0',
 'pytest-assume>=2.4.3,<3.0.0',
 'pytest-sugar>=0.9.6,<0.10.0',
 'requests>=2.28.1,<3.0.0',
 'typer[all]>=0.7.0,<0.8.0']

entry_points = \
{'console_scripts': ['apicase = apicase.script.cli:main']}

setup_kwargs = {
    'name': 'apicase',
    'version': '0.2.0',
    'description': '',
    'long_description': None,
    'author': 'guowenhe',
    'author_email': '18538570410@163.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10.0,<4.0.0',
}


setup(**setup_kwargs)
