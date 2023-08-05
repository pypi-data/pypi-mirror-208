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
    'version': '0.1.1',
    'description': 'Implementation of fsspec for Box file storage',
    'long_description': '# boxfs\n\nImplementation of the [`fsspec`](https://filesystem-spec.readthedocs.io/en/latest/index.html) protocol for [Box](https://www.box.com/overview) content\nmanagement, enabling you to interface with files stored on Box using\nfile-system-like navigation.\n\n## Installation\n\nYou can install `boxfs` from [PyPI](https://pypi.org/project/boxfs/). Use the following\ncommand:\n\n```bash\npip install boxfs\n```\n\n## Example\n\n```python\nimport fsspec\nfrom boxsdk import JWTAuth\n\noauth = JWTAuth.from_settings_file("PATH/TO/JWT_CONFIGURATION.json")\nroot_id = "<ID-of-file-system-root>"\n\n### For simple file access, you can use `fsspec.open`\nwith fsspec.open("box://Documents/test_file.txt", "wb", oauth=oauth, root_id=root_id) as f:\n    f.write("This file was produced using boxfs")\n\n### For more control, you can use `fsspec.filesystem`\nfs = fsspec.filesystem(\'box\', oauth=oauth, root_id=root_id)\n# List directory contents\nfs.ls("Documents")\n# Make new directory\nfs.mkdir("Documents/Test Folder")\n# Remove a directory\nfs.rmdir("Documents/Test Folder")\n\n# Open and write file\nwith fs.open("Documents/test_file.txt", "wb") as f:\n    f.write("This file was updated using boxfs")\n\n# Print file contents\nfs.cat("Documents/test_file.txt")\n# Delete file\nfs.rm("Documents/test_file.txt")\n```\n\n## Creating a Box App\n\nBefore you can use `boxfs`, you will need a Box application through which you can route\nyour API calls. To do so, you can follow the steps for\n["Setup with JWT"](https://developer.box.com/guides/authentication/jwt/jwt-setup/)\nin the Box Developer documentation. The JWT configuration `.json` file that\nyou generate will have to be stored locally and loaded using\n`JWTAuth.from_settings_file`. You also have to add your application\'s\nService Account as a collaborator on the root folder of your choosing, or\nyou will only have access to the Box application\'s files.\n',
    'author': 'Thomas Hunter',
    'author_email': 'boxfs.tehunter@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/IBM/boxfs',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
