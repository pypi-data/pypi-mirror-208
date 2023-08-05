# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['peerai_python_sdk']

package_data = \
{'': ['*']}

install_requires = \
['ipfs-cid>=1.0.0,<2.0.0',
 'numpy>=1.24.3,<2.0.0',
 'onnx-tool>=0.6.4,<0.7.0',
 'onnx>=1.14.0,<2.0.0',
 'onnxruntime>=1.14.1,<2.0.0',
 'requests-toolbelt>=1.0.0,<2.0.0',
 'requests>=2.30.0,<3.0.0',
 'tqdm>=4.65.0,<5.0.0']

setup_kwargs = {
    'name': 'peerai-python-sdk',
    'version': '0.1.1',
    'description': '',
    'long_description': '',
    'author': 'Surat Teerapittayanon',
    'author_email': 'surat@peer-ai.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
