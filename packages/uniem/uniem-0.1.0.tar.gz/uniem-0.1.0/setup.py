# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['uniem']

package_data = \
{'': ['*']}

install_requires = \
['accelerate>=0.19.0,<0.20.0',
 'torch>=2.0.0,<3.0.0',
 'tqdm>=4.65.0,<5.0.0',
 'transformers>=4.28.0,<5.0.0',
 'typer[all]>=0.9.0,<0.10.0']

setup_kwargs = {
    'name': 'uniem',
    'version': '0.1.0',
    'description': 'unified embedding model',
    'long_description': "# uniem\nunified embedding model\n\n# Usage\n\n```python\nfrom uniem import UniEmbedder\n\n\nsentences = ['Hello, World!', '你好，世界！']\nembedder = UniEmbedder()\nembeddings = embedder(sentences)\n```\n\n## Train Your Model\n\n1. create virtual environment\n```bash\nconda create -n uniem python=3.10\n```\n2. install uniem\n```bash\npip install -e .\n```\n3. get help\n```bash\npython scripts/train_medi.py --help\n```\n4. train embedding model\n```bash\npython scripts/train_medi.py <model_path_or_name> <data_file>\n```\n",
    'author': 'wangyuxin',
    'author_email': 'wangyuxin@mokahr.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
