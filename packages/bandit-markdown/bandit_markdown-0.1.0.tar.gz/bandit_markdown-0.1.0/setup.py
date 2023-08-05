# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['bandit_markdown']

package_data = \
{'': ['*']}

install_requires = \
['bandit>=1.7.5,<2.0.0']

entry_points = \
{'console_scripts': ['bandit-markdown = bandit_markdown.main:main']}

setup_kwargs = {
    'name': 'bandit-markdown',
    'version': '0.1.0',
    'description': '',
    'long_description': '# bandit-markdown\n\n`bandit-markdown` is a Python Command Line App to apply the security checking tool [bandit](https://github.com/PyCQA/bandit) on Markdown files to avoid showing code samples with vulnerabilities.\n\n## Installation\n\nYou can install `bandit-markdown` using pip (note the underscore):\n\n```bash\npip install bandit_markdown\n```\n\n## Usage\n\nTo use `bandit-markdown`, you just have to specify a glob of Markdown files.\n\nSmall example:\n\n```bash\nbandit-markdown examples/*.md\n```\n\nThis will run `bandit` on all the Markdown files in the `examples` directory and print the `bandit` report.\n\n## License\n\n`bandit-markdown` is licensed under the MIT License. See the LICENSE file for more information.\n\nCode is mainly based on [flake8-markdown](https://github.com/johnfraney/flake8-markdown/tree/main)\n',
    'author': 'baniasbaabe',
    'author_email': 'banias@hotmail.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/baniasbaabe/bandit-markdown',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
