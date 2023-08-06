# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['woe_scoring',
 'woe_scoring.core',
 'woe_scoring.core.binning',
 'woe_scoring.core.model']

package_data = \
{'': ['*']}

install_requires = \
['joblib>=1.1.0',
 'lxml>=4.8.0',
 'numpy>=1.19.5',
 'pandas>=1.2.2',
 'scikit-learn>=0.24.1',
 'scipy>=1.6.1',
 'statsmodels>=0.12.2']

setup_kwargs = {
    'name': 'woe-scoring',
    'version': '0.10.8',
    'description': 'Weight Of Evidence Transformer and LogisticRegression model with scikit-learn API',
    'long_description': 'None',
    'author': 'Stroganov Kirill',
    'author_email': 'kiraplenkin@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
