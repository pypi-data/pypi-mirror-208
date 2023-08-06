# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cg_pytest_reporter']

package_data = \
{'': ['*']}

install_requires = \
['pytest>=7.3.1']

entry_points = \
{'pytest11': ['cg_pytest_reporter = cg_pytest_reporter.plugin']}

setup_kwargs = {
    'name': 'cg-pytest-reporter',
    'version': '2023.5.17.1137',
    'description': '',
    'long_description': '# cg-pytest-reporter\n',
    'author': 'CodeGrade',
    'author_email': 'info@codegrade.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
