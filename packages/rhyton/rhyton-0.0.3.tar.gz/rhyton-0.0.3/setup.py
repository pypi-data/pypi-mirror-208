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
    'version': '0.0.3',
    'description': 'R to Python transpiler',
    'long_description': '<div id="header" align="center">\n<img src="https://i.ibb.co/9mxMf46/rhyton-logo.png" alt="Rhyton logo"/>\n  <h1>\n    <i>Rhyton</i> - R to Python transpiler\n  </h1>\n</div>\n\n##📜 What is _Rhyton_\n\n__Rhyton__ is a type of ancient Greek drinking vessel that is in the shape of an animal\'s head or horn and has a hole in the bottom for pouring the liquid. It was often used in religious ceremonies or feasts.\n\nThe name came after combination of language names: _R_ and _Python_\n\nThis library helps you to move R codebase to Python. Right now it supports conversion of _math equations_, _expressions_, _conditions_, _function definitions_ and _calls_\n\n## 🧲 Installation\nThe project is published on [__PyPi__](https://pypi.org/project/rhyton/), so you can install it via __pip__\n\n```shell\n$: pip install rhyton\n```\n\n## 🚀 Launch\nUse _transpile_ or _transpile_file_ to translate your __R__ code\n\n```python\nfrom rhyton import transpile, transpile_file\n\ntranspile(\'x <- 7\') # returns transpiled string\n\n# or\n\ntranspile_file(\n  in_path=\'<path to your R file>.r\', \n  out_path=\'<Path to generated Python file>.py\'\n)\n\n```\n\n## 🛠 How it works\n__Rhyton__ uses tree-sitter under the hood, to compute _AST_ (Abstract Syntax Tree), after that it converts it to new _AST_ that is valid for Python. After that it generates a code, using [_ast module_](https://docs.python.org/3/library/ast.html) and [_astor_](https://astor.readthedocs.io/en/latest/)\n\n## 📊 Feature plan\n* ✅ Add tree parsers\n* ✅ Semantic analysis for _AST_\n  * ✅ Statements and expressions\n  * ✅ Math operations\n  * ✅ Conditions: _if_, _else_\n  * ✅ Function definitions\n  * ✅ Function calls\n  * ❌ Cycles while and for\n  * ❌ Arrays and operations\n  * ❌ Function analogs\n  * ❌ Import statements \n  * ❌ Nested transpilation\n\n* ✅ Package demo publication\n* ✅ Project site\n',
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
