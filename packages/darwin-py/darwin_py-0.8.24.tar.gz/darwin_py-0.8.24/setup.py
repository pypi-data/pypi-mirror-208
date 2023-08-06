# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['darwin',
 'darwin.dataset',
 'darwin.exporter',
 'darwin.exporter.formats',
 'darwin.future',
 'darwin.future.core',
 'darwin.future.core.types',
 'darwin.future.core.utils',
 'darwin.future.data_objects',
 'darwin.future.exceptions',
 'darwin.future.meta',
 'darwin.future.meta.queries',
 'darwin.future.meta.types',
 'darwin.future.tests',
 'darwin.future.tests.core',
 'darwin.future.tests.data_objects',
 'darwin.future.tests.meta',
 'darwin.future.tests.meta.queries',
 'darwin.importer',
 'darwin.importer.formats',
 'darwin.torch',
 'darwin.utils',
 'darwin.version']

package_data = \
{'': ['*']}

install_requires = \
['argcomplete>=2.0.0,<3.0.0',
 'deprecation>=2.1.0,<3.0.0',
 'humanize>=4.4.0,<5.0.0',
 'jsonschema>=4.0.0',
 'mpire>=2.7.0,<3.0.0',
 'numpy',
 'orjson>=3.8.5,<4.0.0',
 'pillow>=9.4.0,<10.0.0',
 'pydantic>=1.10.4,<2.0.0',
 'pyyaml>=5.1',
 'requests>=2.28.1,<3.0.0',
 'rich>=13.0.1,<14.0.0',
 'toml>=0.10.2,<0.11.0',
 'tqdm>=4.64.1,<5.0.0',
 'types-pyyaml>=6.0.12.9,<7.0.0.0',
 'types-requests>=2.28.11.8,<3.0.0.0',
 'upolygon==0.1.10']

extras_require = \
{':(python_full_version >= "3.8.1" and python_version < "3.11") and (extra == "dev" or extra == "test")': ['flake8-pyproject>=1.2.2,<2.0.0'],
 ':(python_full_version >= "3.8.1" and python_version < "3.11") and (extra == "dev")': ['flake8>=6.0.0,<7.0.0'],
 ':(python_full_version >= "3.8.1" and python_version < "3.11") and (extra == "ml")': ['scikit-learn>=1.2.0,<2.0.0'],
 ':(python_full_version >= "3.8.1") and (extra == "medical")': ['nibabel>=5.0.0,<6.0.0'],
 ':extra == "dev"': ['black>=22.12.0,<23.0.0',
                     'isort>=5.11.4,<6.0.0',
                     'mypy>=0.991,<0.992',
                     'debugpy>=1.6.5,<2.0.0'],
 ':extra == "dev" or extra == "test"': ['responses>=0.22.0,<0.23.0',
                                        'pytest>=7.2.1,<8.0.0',
                                        'pytest-describe>=2.0.1,<3.0.0'],
 ':extra == "medical"': ['connected-components-3d>=3.10.3,<4.0.0'],
 ':extra == "ml"': ['torch>=1.13.1,<2.0.0', 'torchvision>=0.14.1,<0.15.0'],
 ':python_version < "3.7"': ['dataclasses>=0.8,<0.9']}

entry_points = \
{'console_scripts': ['darwin = darwin.cli:main']}

setup_kwargs = {
    'name': 'darwin-py',
    'version': '0.8.24',
    'description': 'Library and command line interface for darwin.v7labs.com',
    'long_description': '# V7 Darwin Python SDK\n\nOfficial library to manage datasets along with\n[V7 Darwin annotation platform](https://darwin.v7labs.com).\n\nDarwin-py can both be used from the [command line](#usage-as-a-command-line-interface-cli) and as a [python library](#usage-as-a-python-library).\n\nMain functions are (but not limited to):\n\n- Client authentication\n- Listing local and remote datasets\n- Create/remove datasets\n- Upload/download data to/from remote datasets\n- Direct integration with PyTorch dataloaders\n\nSupport tested for python 3.8.\n\n## Installation\n\n```\npip install darwin-py\n```\n\nYou can now type `darwin` in your terminal and access the command line interface.\n\nIf you wish to use the PyTorch bindings, then you can use the `ml` flag to install all the additional requirements\n\n```\npip install darwin-py[ml]\n```\n\nTo run test, first install the `test` extra package\n\n```\npip install darwin-py[test]\n```\n\n---\n\n## Usage as a Command Line Interface (CLI)\n\nOnce installed, `darwin` is accessible as a command line tool.\nA useful way to navigate the CLI usage is through the help command `-h/--help` which will\nprovide additional information for each command available.\n\n### Client Authentication\n\nTo perform remote operations on Darwin you first need to authenticate.\nThis requires a [team-specific API-key](https://darwin.v7labs.com/?settings=api-keys).\nIf you do not already have a Darwin account, you can [contact us](https://www.v7labs.com/contact) and we can set one up for you.\n\nTo start the authentication process:\n\n```\n$ darwin authenticate\nAPI key:\nMake example-team the default team? [y/N] y\nDatasets directory [~/.darwin/datasets]:\nAuthentication succeeded.\n```\n\nYou will be then prompted to enter your API-key, whether you want to set the corresponding team as\ndefault and finally the desired location on the local file system for the datasets of that team.\nThis process will create a configuration file at `~/.darwin/config.yaml`.\nThis file will be updated with future authentications for different teams.\n\n### Listing local and remote datasets\n\nLists a summary of local existing datasets\n\n```\n$ darwin dataset local\nNAME            IMAGES     SYNC_DATE         SIZE\nmydataset       112025     yesterday     159.2 GB\n```\n\nLists a summary of remote datasets accessible by the current user.\n\n```\n$ darwin dataset remote\nNAME                       IMAGES     PROGRESS\nexample-team/mydataset     112025        73.0%\n```\n\n### Create/remove a dataset\n\nTo create an empty dataset remotely:\n\n```\n$ darwin dataset create test\nDataset \'test\' (example-team/test) has been created.\nAccess at https://darwin.v7labs.com/datasets/579\n```\n\nThe dataset will be created in the team you\'re authenticated for.\n\nTo delete the project on the server:\n\n```\n$ darwin dataset remove test\nAbout to delete example-team/test on darwin.\nDo you want to continue? [y/N] y\n```\n\n### Upload/download data to/from a remote dataset\n\nUploads data to an existing remote project.\nIt takes the dataset name and a single image (or directory) with images/videos to upload as\nparameters.\n\nThe `-e/--exclude` argument allows to indicate file extension/s to be ignored from the data_dir.\ne.g.: `-e .jpg`\n\nFor videos, the frame rate extraction rate can be specified by adding `--fps <frame_rate>`\n\nSupported extensions:\n\n- Video files: [`.mp4`, `.bpm`, `.mov` formats].\n- Image files [`.jpg`, `.jpeg`, `.png` formats].\n\n```\n$ darwin dataset push test /path/to/folder/with/images\n100%|████████████████████████| 2/2 [00:01<00:00,  1.27it/s]\n```\n\nBefore a dataset can be downloaded, a release needs to be generated:\n\n```\n$ darwin dataset export test 0.1\nDataset test successfully exported to example-team/test:0.1\n```\n\nThis version is immutable, if new images / annotations have been added you will have to create a new release to included them.\n\nTo list all available releases\n\n```\n$ darwin dataset releases test\nNAME                           IMAGES     CLASSES                   EXPORT_DATE\nexample-team/test:0.1               4           0     2019-12-07 11:37:35+00:00\n```\n\nAnd to finally download a release.\n\n```\n$ darwin dataset pull test:0.1\nDataset example-team/test:0.1 downloaded at /directory/choosen/at/authentication/time.\n```\n\n---\n\n## Usage as a Python library\n\nThe framework is designed to be usable as a standalone python library.\nUsage can be inferred from looking at the operations performed in `darwin/cli_functions.py`.\nA minimal example to download a dataset is provided below and a more extensive one can be found in\n[darwin_demo.py]([./darwin_demo.py](https://github.com/v7labs/darwin-py/blob/master/darwin_demo.py).\n\n```python\nfrom darwin.client import Client\n\nclient = Client.local() # use the configuration in ~/.darwin/config.yaml\ndataset = client.get_remote_dataset("example-team/test")\ndataset.pull() # downloads annotations and images for the latest exported version\n```\n\nFollow [this guide](https://docs.v7labs.com/docs/loading-a-dataset-in-python) for how to integrate darwin datasets directly in PyTorch.\n',
    'author': 'V7',
    'author_email': 'info@v7labs.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://docs.v7labs.com/reference/getting-started-2',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7.0,<3.12',
}


setup(**setup_kwargs)
