# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['crispr_shrinkage', 'crispr_shrinkage.framework']

package_data = \
{'': ['*']}

install_requires = \
['matplotlib>=3.6.3,<4.0.0', 'numpy>=1.24.1,<2.0.0', 'scipy>=1.10.0,<2.0.0']

setup_kwargs = {
    'name': 'crispr-shrinkage',
    'version': '0.1.67',
    'description': '',
    'long_description': '',
    'author': 'Basheer Becerra',
    'author_email': 'bbecerra@fas.harvard.edu',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.12',
}


setup(**setup_kwargs)
