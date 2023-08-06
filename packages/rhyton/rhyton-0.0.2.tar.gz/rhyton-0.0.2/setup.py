# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['rhyton']

package_data = \
{'': ['*'], 'rhyton': ['transpile_test/*']}

install_requires = \
['astor>=0.8.1,<0.9.0',
 'pydocstyle>=6.3.0,<7.0.0',
 'rich>=13.3.5,<14.0.0',
 'sexpdata>=1.0.0,<2.0.0',
 'tree-sitter-languages>=1.5.0,<2.0.0',
 'tree-sitter>=0.20.1,<0.21.0']

setup_kwargs = {
    'name': 'rhyton',
    'version': '0.0.2',
    'description': 'R to Python transpiler',
    'long_description': '\n# Rhyton - R to Python transpiler\n\nThe library that helps you to move R codebase to Python\n',
    'author': 'Dmitriy Din',
    'author_email': 'dmitriy1d01@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
