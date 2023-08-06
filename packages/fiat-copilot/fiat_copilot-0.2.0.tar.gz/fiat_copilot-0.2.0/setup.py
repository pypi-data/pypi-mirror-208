# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fiat_copilot',
 'fiat_copilot.examples.assets',
 'fiat_copilot.examples.serving',
 'fiat_copilot.examples.storage',
 'fiat_copilot.examples.training',
 'fiat_copilot.serving',
 'fiat_copilot.trainer',
 'fiat_copilot.utils',
 'fiat_copilot.workflow']

package_data = \
{'': ['*']}

install_requires = \
['cos-python-sdk-v5>=1.9.24,<2.0.0',
 'dagit>=1.3.4,<2.0.0',
 'dagster>=1.3.4,<2.0.0',
 'esdk-obs-python>=3.22.2,<4.0.0',
 'oss2>=2.17.0,<3.0.0',
 'ray[default]>=2.4.0,<3.0.0',
 'xgboost-ray>=0.1.15,<0.2.0',
 'xgboost>=1.7.5,<2.0.0']

setup_kwargs = {
    'name': 'fiat-copilot',
    'version': '0.2.0',
    'description': '🧑\u200d🚀 - Fiat Copilot is a variety of utilities to smooth your ML development workflow.',
    'long_description': '# Fiat-Copilot\n\n#### Description\n🧑\u200d🚀 - Fiat Copilot is a variety of utilities to smooth your ML development workflow.\n',
    'author': 'ValerioL29',
    'author_email': 'cheng2029@foxmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
