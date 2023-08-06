# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['kolena',
 'kolena._api',
 'kolena._api.v1',
 'kolena._utils',
 'kolena._utils.dataframes',
 'kolena.classification',
 'kolena.classification.multiclass',
 'kolena.detection',
 'kolena.detection._internal',
 'kolena.fr',
 'kolena.workflow',
 'kolena.workflow.metrics']

package_data = \
{'': ['*']}

install_requires = \
['Pillow>=9.1.1,<10.0.0',
 'Shapely>=1.8.5,<2.0.0',
 'click>=8.1.3,<9.0.0',
 'dacite>=1.6',
 'deprecation>=2.1.0,<3.0.0',
 'pandera>=0.9.0',
 'pyarrow>=8',
 'pydantic>=1.8',
 'requests-toolbelt',
 'requests>=2.20,<2.30',
 'retrying>=1.3.3,<2.0.0',
 'termcolor>=1.1.0,<2.0.0',
 'tqdm>=4,<5']

extras_require = \
{':python_version < "3.8"': ['importlib-metadata<5.0',
                             'typing-extensions>=4.5.0,<5.0.0'],
 ':python_version >= "3.11"': ['numpy>=1.23', 'pandas>=1.5,<1.6'],
 ':python_version >= "3.7" and python_version < "3.11"': ['numpy>=1.19',
                                                          'pandas>=1.1,<1.6']}

entry_points = \
{'console_scripts': ['kolena = kolena._utils.cli:run']}

setup_kwargs = {
    'name': 'kolena-client',
    'version': '0.69.0',
    'description': "Client for Kolena's machine learning (ML) testing and debugging platform.",
    'long_description': '<p align="center">\n  <img src="https://app.kolena.io/api/developer/docs/html/_static/wordmark-purple.svg" width="400" alt="Kolena" />\n</p>\n\n<p align=\'center\'>\n  <a href="https://pypi.python.org/pypi/kolena"><img src="https://img.shields.io/pypi/v/kolena" /></a>\n  <a href="https://www.apache.org/licenses/LICENSE-2.0"><img src="https://img.shields.io/pypi/l/kolena" /></a>\n  <a href="https://github.com/kolenaIO/kolena/actions"><img src="https://img.shields.io/github/checks-status/kolenaIO/kolena/trunk" /></a>\n  <a href="https://codecov.io/gh/kolenaIO/kolena" ><img src="https://codecov.io/gh/kolenaIO/kolena/branch/trunk/graph/badge.svg?token=8WOY5I8SF1"/></a>\n  <a href="https://docs.kolena.io"><img src="https://img.shields.io/badge/resource-docs-6434c1" /></a>\n</p>\n\n---\n\n[Kolena](https://www.kolena.io) is a comprehensive machine learning testing and debugging platform to surface hidden\nmodel behaviors and take the mystery out of model development. Kolena helps you:\n\n- Perform high-resolution model evaluation\n- Understand and track behavioral improvements and regressions\n- Meaningfully communicate model capabilities\n- Automate model testing and deployment workflows\n\nThis `kolena` package contains the Python client library for programmatic interaction with the Kolena ML testing\nplatform.\n\n## Documentation\n\nVisit [docs.kolena.io](https://docs.kolena.io/) for tutorial and usage documentation and the\n[API Reference](https://app.kolena.io/api/developer/docs/html/index.html) for detailed `kolena` typing and\nfunction documentation.\n',
    'author': 'Kolena Engineering',
    'author_email': 'eng@kolena.io',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://kolena.io',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7.1,<3.12',
}


setup(**setup_kwargs)
