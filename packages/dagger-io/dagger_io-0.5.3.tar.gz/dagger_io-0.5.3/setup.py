# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['dagger', 'dagger.api', 'dagger.engine', 'dagger.server', 'dagger.transport']

package_data = \
{'': ['*']}

install_requires = \
['anyio>=3.6.2',
 'attrs>=22.1.0',
 'beartype>=0.11.0',
 'cattrs>=22.2.0',
 'gql>=3.4.0',
 'graphql-core>=3.2.3',
 'httpx>=0.23.1',
 'platformdirs>=2.6.2',
 'rich>=12.6.0',
 'typer[all]>=0.6.1',
 'typing_extensions>=4.4.0']

extras_require = \
{'server': ['strawberry-graphql>=0.133.5']}

setup_kwargs = {
    'name': 'dagger-io',
    'version': '0.5.3',
    'description': 'A client package for running Dagger pipelines in Python.',
    'long_description': '# Dagger Python SDK\n\n[![PyPI Version](https://img.shields.io/pypi/v/dagger-io)](https://pypi.org/project/dagger-io/) \n[![Conda Version](https://img.shields.io/conda/vn/conda-forge/dagger-io.svg)](https://anaconda.org/conda-forge/dagger-io)\n[![Supported Python Versions](https://img.shields.io/pypi/pyversions/dagger-io.svg)](https://pypi.org/project/dagger-io/)\n[![License](https://img.shields.io/pypi/l/dagger-io.svg)](https://pypi.python.org/pypi/dagger-io)\n[![Code style](https://img.shields.io/badge/code%20style-black-black.svg)](https://github.com/psf/black)\n[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v1.json)](https://github.com/charliermarsh/ruff)\n\nA client package for running [Dagger](https://dagger.io/) pipelines.\n\n## What is the Dagger Python SDK?\n\nThe Dagger Python SDK contains everything you need to develop CI/CD pipelines in Python, and run them on any OCI-compatible container runtime.\n\n## Requirements\n\n- Python 3.10 or later\n- [Docker](https://docs.docker.com/engine/install/), or another OCI-compatible container runtime\n\nA compatible version of the  [Dagger CLI](https://docs.dagger.io/cli) is automatically downloaded and run by the SDK for you, although it’s possible to manage it manually.\n\n## Installation\n\nFrom [PyPI](https://pypi.org/project/dagger-io/), using `pip`:\n\n```shell\npip install dagger-io\n```\n\nYou can also install via [Conda](https://anaconda.org/conda-forge/dagger-io), from the [conda-forge](https://conda-forge.org/docs/user/introduction.html#how-can-i-install-packages-from-conda-forge) channel:\n\n```shell\nconda install dagger-io\n```\n\n## Example\n\nCreate a `main.py` file:\n\n```python\nimport sys\n\nimport anyio\nimport dagger\n\n\nasync def main(args: list[str]):\n    async with dagger.Connection() as client:\n        # build container with cowsay entrypoint\n        ctr = (\n            client.container()\n            .from_("python:alpine")\n            .with_exec(["pip", "install", "cowsay"])\n            .with_entrypoint(["cowsay"])\n        )\n\n        # run cowsay with requested message\n        result = await ctr.with_exec(args).stdout()\n\n    print(result)\n\n\nanyio.run(main, sys.argv[1:])\n```\n\nRun with:\n\n```console\n$ python main.py "Simple is better than complex"\n  _____________________________\n| Simple is better than complex |\n  =============================\n                             \\\n                              \\\n                                ^__^\n                                (oo)\\_______\n                                (__)\\       )\\/\\\n                                    ||----w |\n                                    ||     ||\n```\n\n> **Note**\n> It may take a while for it to finish, especially on first run with cold cache.\n\nIf you need to debug, you can stream the logs from the engine with the `log_output`  config:\n\n```python\nconfig = dagger.Config(log_output=sys.stderr)\nasync with dagger.Connection(config) as client:\n    ...\n```\n\n## Learn more\n\n- [Documentation](https://docs.dagger.io/sdk/python)\n- [API Reference](https://dagger-io.readthedocs.org)\n- [Source code](https://github.com/dagger/dagger/tree/main/sdk/python)\n\n## Development\n\nThis library is maintained with [Poetry](https://python-poetry.org/docs/).\n\nIf you already have a [Python 3.10 or later](https://docs.python.org/3/using/index.html) interpreter in your `$PATH`, you can let [Poetry manage](https://python-poetry.org/docs/basic-usage/#using-your-virtual-environment) the [virtual environment](https://packaging.python.org/en/latest/tutorials/installing-packages/#creating-virtual-environments) automatically. Otherwise you need to activate it first, before installing dependencies:\n\n```shell\npoetry install\n```\n\nThe following commands are available:\n- `poe test`: Run tests.\n- `poe fmt`: Re-format code following common styling conventions.\n- `poe lint`: Check for linting violations.\n- `poe generate`: Regenerate API client after changes to the codegen.\n- `poe docs`: Build reference docs locally.\n\n### Engine changes\n\nTesting and regenerating the client may fail if there’s changes in the engine code that haven’t been released yet. \n\nThe simplest way to run those commands locally with the most updated engine version is to build it using [Dagger’s CI pipelines](https://github.com/dagger/dagger/blob/main/internal/mage/sdk/python.go) :\n\n```shell\n../../hack/make sdk:python:test\n../../hack/make sdk:python:generate\n```\n\nYou can also build the CLI and use it directly within the Python SDK:\n\n```shell\n../../hack/dev poe test\n```\n\nOr build it separately and tell the SDK to use it directly (or any other CLI binary):\n\n```shell\n../../hack/make\n_EXPERIMENTAL_DAGGER_CLI_BIN=../../bin/dagger poe test\n```\n\n',
    'author': 'Dagger',
    'author_email': 'hello@dagger.io',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://dagger.io',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
