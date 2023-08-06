# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src', 'fenlmagic': 'src/fenlmagic', 'validate': 'vendor/validate'}

packages = \
['fenlmagic',
 'kaskada',
 'kaskada.api',
 'kaskada.kaskada.v1alpha',
 'kaskada.kaskada.v2alpha',
 'validate']

package_data = \
{'': ['*']}

install_requires = \
['certifi>=2022.12.7,<2023.0.0',
 'domonic>=0.9.11,<0.10.0',
 'googleapis-common-protos>=1.58.0,<2.0.0',
 'grpcio-status>=1.51.1,<2.0.0',
 'grpcio>=1.51.1,<2.0.0',
 'html5lib>=1.1,<2.0',
 'ipython==7.34.0',
 'pandas>=1.3,<1.4',
 'pyarrow>=10.0.1,<11.0.0',
 'pygithub>=1.57,<2.0',
 'requests>=2.28.2,<3.0.0',
 'tqdm>=4.64.1,<5.0.0']

setup_kwargs = {
    'name': 'kaskada',
    'version': '0.2.0',
    'description': 'A client library for the Kaskada time travel machine learning service',
    'long_description': '# Kaskada SDK\n\n## Developer Instructions\nThe package uses Poetry to develop and build.\n\n1. Install Pyenv [Pyenv Documentation](https://github.com/pyenv/pyenv)\n1. Install Python 3.9.16: `$ pyenv install 3.9.16`\n1. Install Poetry [Poetry Documentation](https://python-poetry.org/docs/)\n1. Install dependences: `$ poetry install`\n\n### Run tasks\nThe package uses [`poethepoet`](https://github.com/nat-n/poethepoet) for running tasks\n\n#### Test Task\nTo run tests: `$ poetry run poe test` \n\n#### Check Style Task\nTo check the style: `$ poetry run poe style`\n\n#### Format Task\nTo auto-format (isort + black): `$ poetry run poe format`\n\n#### Check Static Type Task\nTo perform static type analysis (mypy): `$ poetry run poe types`\n\n#### Lint Task\nTo run the linter (pylint): `$ poetry run poe lint`\n\n#### Generate documentation \nWe use Sphinx and rely on autogeneration extensions within Sphinx to read docstrings and \ngenerate an HTML formatted version of the codes documentation. \n\n* `poetry run poe docs` : generates and builds the docs \n* `poetry run poe docs-generate` : generates the docs (.rst files)\n* `poetry run poe docs-build` : builds the HTML rendered version of the generated docs (from .rst to .html)\n\nThe generated HTML is located inside `docs/build`. Load `docs/build/index.html` in your browser to see the HTML rendered output. \n\n## Using the Client from Jupyter\n\n#### Install Jupyter\nTo install Jupyter: `$ pip install notebook`\n\n#### Build the Client\nTo build the client: `$ poetry build`\n\n#### Install the Client\nTo install the client: `$ pip install dist/*.whl`\n\n#### Open a Jupyter Notebook\nTo open a notebook: `$ jupyter notebook`\n',
    'author': 'Kaskada',
    'author_email': 'maintainers@kaskada.io',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.2,<4.0.0',
}


setup(**setup_kwargs)
