# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['boxfs']

package_data = \
{'': ['*']}

install_requires = \
['boxsdk[jwt]>=3.7,<4.0', 'fsspec>=2023.4', 'urllib3<2']

entry_points = \
{'fsspec.specs': ['box = boxfs.boxfs:BoxFileSystem']}

setup_kwargs = {
    'name': 'boxfs',
    'version': '0.1a1',
    'description': 'Box File System',
    'long_description': 'None',
    'author': 'Thomas Hunter',
    'author_email': 'boxfs.tehunter@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
