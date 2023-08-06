# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pylint_plugin_utils']

package_data = \
{'': ['*']}

install_requires = \
['pylint>=1.7']

setup_kwargs = {
    'name': 'pylint-plugin-utils',
    'version': '0.8',
    'description': 'Utilities and helpers for writing Pylint plugins',
    'long_description': '# pylint-plugin-utils\n\n## Status\n\n[![Build Status](https://github.com/PyCQA/pylint-plugin-utils/actions/workflows/ci.yaml/badge.svg?branch=master)](https://github.com/PyCQA/pylint-plugin-utils/actions)\n[![Coverage Status](https://coveralls.io/repos/github/PyCQA/pylint-plugin-utils/badge.svg?branch=master)](https://coveralls.io/github/PyCQA/pylint-plugin-utils?branch=master)\n[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)\n[![Pypi Package version](https://img.shields.io/pypi/v/pylint-plugin-utils.svg)](https://pypi.python.org/pypi/pylint-plugin-utils)\n\n# About\n\nUtilities and helpers for writing Pylint plugins. This is not a direct Pylint plugin, but rather a set of tools and functions used by other plugins such as [pylint-django](https://github.com/PyCQA/pylint-django) and [pylint-celery](https://github.com/PyCQA/pylint-celery).\n\n# Testing\nCreate virtualenv:\n```bash\npython3.8 -m venv .pylint-plugin-utils\nsource .pylint-plugin-utils/bin/activate\npip install --upgrade pip setuptools\n```\n\nWe use [tox](https://tox.readthedocs.io/en/latest/) for running the test suite. You should be able to install it with:\n```bash\npip install tox pytest\n```\n\nTo run the test suite for a particular Python version, you can do:\n```bash\ntox -e py38\n```\n\nTo run individual tests with ``tox``, you can do:\n```bash\ntox -e py38 -- -k test_linter_should_be_pickleable\n```\n\nWe use ``pytest`` for testing ``pylint``, which you can use without using ``tox`` for a faster development cycle.\n\nIf you want to run tests on a specific portion of the code with [pytest](https://docs.pytest.org/en/latest/), [pytest-cov](https://pypi.org/project/pytest-cov/) and your local python version::\n```bash\npip install pytest-cov\n# Everything:\npython3 -m pytest tests/ --cov=pylint_plugin_utils\ncoverage html\n```\n\n# License\n\n`pylint-plugin-utils` is available under the GPLv2 License.\n',
    'author': 'Carl Crowder',
    'author_email': 'git@carlcrowder.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/PyCQA/pylint-plugin-utils',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
