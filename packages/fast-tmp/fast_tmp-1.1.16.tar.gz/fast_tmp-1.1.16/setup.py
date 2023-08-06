# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fast_tmp',
 'fast_tmp.admin',
 'fast_tmp.amis',
 'fast_tmp.amis.forms',
 'fast_tmp.amis.view',
 'fast_tmp.conf',
 'fast_tmp.contrib',
 'fast_tmp.contrib.auth',
 'fast_tmp.contrib.pydantic',
 'fast_tmp.contrib.tortoise',
 'fast_tmp.jinja_extension',
 'fast_tmp.site',
 'fast_tmp.utils',
 'fast_tmp_cli',
 'fast_tmp_cli.tpl.project.{{cookiecutter.project_slug}}',
 'fast_tmp_cli.tpl.project.{{cookiecutter.project_slug}}.tests',
 'fast_tmp_cli.tpl.project.{{cookiecutter.project_slug}}.{{cookiecutter.project_slug}}']

package_data = \
{'': ['*'],
 'fast_tmp.admin': ['templates/*'],
 'fast_tmp_cli': ['tpl/project/*', 'tpl/static/*', 'tpl/static/static/*'],
 'fast_tmp_cli.tpl.project.{{cookiecutter.project_slug}}': ['static/*',
                                                            'static/css/*',
                                                            'static/img/*',
                                                            'static/js/*']}

install_requires = \
['asgiref>=3.5.2,<4.0.0',
 'fastapi>=0.95.0,<0.96.0',
 'python-dotenv>=1.0.0,<2.0.0',
 'python-jose>=3.3.0,<4.0.0',
 'python-multipart>=0.0.6,<0.0.7',
 'toml>=0.10.2,<0.11.0',
 'tortoise-orm>=0.19.2,<0.20.0',
 'typer>=0.7.0,<0.8.0']

entry_points = \
{'console_scripts': ['fast-tmp = fast_tmp_cli:main']}

setup_kwargs = {
    'name': 'fast-tmp',
    'version': '1.1.16',
    'description': 'fastapi tortoise amis admin',
    'long_description': 'None',
    'author': 'Chise1',
    'author_email': 'chise123@live.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/Chise1/fast-tmp',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
