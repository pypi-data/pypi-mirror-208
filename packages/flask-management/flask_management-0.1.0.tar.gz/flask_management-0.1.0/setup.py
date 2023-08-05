# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['flask_management',
 'flask_management.templates',
 'flask_management.templates.project',
 'flask_management.templates.project.{{ cookiecutter.folder_name }}.tests',
 'flask_management.templates.project.{{ cookiecutter.folder_name }}.{{ '
 'cookiecutter.app_name }}']

package_data = \
{'': ['*'],
 'flask_management.templates.project': ['{{ cookiecutter.folder_name }}/*']}

install_requires = \
['cookiecutter>=1.7.2', 'pydantic[email]>=1.7.2', 'typer']

entry_points = \
{'console_scripts': ['flaskapi = flask_management.main:app']}

setup_kwargs = {
    'name': 'flask-management',
    'version': '0.1.0',
    'description': '',
    'long_description': '# flask-management\n\n## How to use :\n\nflaskapi your-project-name\n',
    'author': 'huangsong',
    'author_email': 'huangsong@leyantech.com',
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
