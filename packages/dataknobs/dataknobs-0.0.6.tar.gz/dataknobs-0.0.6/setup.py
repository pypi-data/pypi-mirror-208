# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dataknobs', 'dataknobs.structures', 'dataknobs.utils', 'dataknobs.xization']

package_data = \
{'': ['*']}

install_requires = \
['beautifulsoup4>=4.11.1,<5.0.0',
 'json-stream>=2.1.1,<3.0.0',
 'lxml>=4.9.2,<5.0.0',
 'more-itertools>=9.0.0,<10.0.0',
 'nltk>=3.7,<4.0',
 'numpy>=1.23.3,<2.0.0',
 'pandas>=1.5.0,<2.0.0',
 'psycopg2-binary>=2.9.3,<3.0.0',
 'python-dotenv>=0.21.0,<0.22.0',
 'requests>=2.28.1,<3.0.0',
 'scikit-learn>=1.2.1,<2.0.0']

setup_kwargs = {
    'name': 'dataknobs',
    'version': '0.0.6',
    'description': 'Useful implementations of data structures and design patterns for AI knowledge bases.',
    'long_description': 'DataKnobs\n=============================\n\n## Description\n\nUseful implementations of data structures and design patterns for knowledge bases and AI, or the knobs and levers for fine-tuning and leveraging your data.\n\nThis repo also serves as a template or sandbox for development, experimentation, and testing of general data structures, algorithms, and utilities for DS, AI, ML, and NLP.\n\nProvides connectors for other popular text and data processing packages like:\n  * numpy and pandas\n  * nltk\n  * wordnet\n  * postgres\n  * elasticsearch\n\n## General project information\n\nThe purpose of this project is:\n\n  * To provide dependable implementations of useful data structures.\n  * To show examples of design patterns and ways to apply AI concepts.\n  * To prototype tools for delivering a robust DS/AI/ML/NLP utilities library package.\n  * To facilitate interactive development, demonstration, visualization, and testing of the library components via jupter notebooks and/or scripts.\n\n## Installation and Usage\n\n```bash/python\n% pip install dataknobs\n% python\n>>> import dataknobs as dk\n>>> ...\n```\n\n\n## Development\n\n### Development machine prerequisites\n\nThe following minimum configuration should exist for development:\n\n  * tox\n  * pyenv\n     * pyenv install 3.9\n  * poetry\n\nWith optional:\n\n  * docker\n  * bash\n\nBy convention, a data directory can be leveraged for development that is mounted as a shared volumne in Docker as /data. This has the default of $HOME/data, but can be overridden with the DATADIR environment variable.\n\n\n### Development quickstart guide\n\n  * In a terminal, clone the repo and cd into the project directory.\n\n#### Testing\n\n  * Tests and Lint: "tox"\n  * Just unit tests: "tox -e tests"\n  * Just lint: "tox -e lint"\n\n#### Using docker\n\n  * Development:\n```\n% tox -e dev\n# poetry shell\n# python\n```\n\n  * Notebook:\n    * execute "tox -e nb"\n      * copy/paste url into browser\n\n#### Using virtual environments\n\n  * Development:\n    * Manual: source ".project_vars", poetry install, poetry shell\n    * Automated: execute "bin/start_dev.sh"  (requires "/bin/bash" on your machine)\n\n  * Notebook:\n    * execute "bin/start_notebook.sh"\n      * copy/paste url into browser\n',
    'author': 'Spence Koehler',
    'author_email': 'KoehlerSB747@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
