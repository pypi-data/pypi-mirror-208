# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['noisy_outlier', 'noisy_outlier.hyperopt', 'noisy_outlier.model']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.24.3,<2.0.0', 'scikit-learn>=1.2.2,<2.0.0']

setup_kwargs = {
    'name': 'noisy-outlier',
    'version': '0.1.5',
    'description': 'Self-Supervised Learning for Outlier Detection',
    'long_description': None,
    'author': 'JanDiers',
    'author_email': 'jan.diers@uni-jena.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
