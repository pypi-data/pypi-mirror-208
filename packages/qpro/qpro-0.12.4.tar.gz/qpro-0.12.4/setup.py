# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['QuickProject']

package_data = \
{'': ['*']}

modules = \
['lang']
install_requires = \
['GitPython>=3.1.31,<4.0.0',
 'inquirer-rhy>=0.1.2,<0.2.0',
 'langsrc>=0.0.8,<0.0.9',
 'pyperclip>=1.8.2,<2.0.0',
 'rich>=13.3.5,<14.0.0']

entry_points = \
{'console_scripts': ['Qpro = QuickProject.Qpro:main',
                     'qrun = QuickProject.qrun:main']}

setup_kwargs = {
    'name': 'qpro',
    'version': '0.12.4',
    'description': 'Small but powerful command line APP framework',
    'long_description': '# QuickProject\n\n> Do you know how to write Python functions? \n\nYes! \n\n> Then you now know how to build command-line applications!\n\n## [Docs](https://qpro-doc.rhythmlian.cn/)\n',
    'author': 'Rhythmicc',
    'author_email': 'rhythmlian.cn@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'py_modules': modules,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
