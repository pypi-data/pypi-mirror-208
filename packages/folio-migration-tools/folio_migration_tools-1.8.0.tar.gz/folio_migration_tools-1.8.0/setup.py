# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['folio_migration_tools',
 'folio_migration_tools.mapping_file_transformation',
 'folio_migration_tools.marc_rules_transformation',
 'folio_migration_tools.migration_tasks',
 'folio_migration_tools.test_infrastructure',
 'folio_migration_tools.transaction_migration']

package_data = \
{'': ['*']}

install_requires = \
['argparse-prompt>=0.0.5,<0.0.6',
 'deepdiff>=6.2.3,<7.0.0',
 'defusedxml>=0.7.1,<0.8.0',
 'folio-uuid>=0.2.8,<0.3.0',
 'folioclient>=0.50.0,<0.51.0',
 'httpx>=0.23.3,<0.24.0',
 'pyaml>=21.10.1,<22.0.0',
 'pydantic>=1.10.2,<2.0.0',
 'pyhumps>=3.7.3,<4.0.0',
 'pymarc>=4.2.1,<5.0.0',
 'python-dateutil>=2.8.2,<3.0.0']

setup_kwargs = {
    'name': 'folio-migration-tools',
    'version': '1.8.0',
    'description': 'A tool allowing you to migrate data from legacy ILS:s (Library systems) into FOLIO LSP',
    'long_description': '# FOLIO Migration Tools\n![example workflow](https://github.com/FOLIO-FSE/MARC21-To-FOLIO/actions/workflows/python-app.yml/badge.svg)[![codecov](https://codecov.io/gh/FOLIO-FSE/folio_migration_tools/branch/main/graph/badge.svg?token=ZQL5ILWWGT)](https://codecov.io/gh/FOLIO-FSE/folio_migration_tools)   [![readthedocs](https://readthedocs.org/projects/docs/badge/?version=latest)](https://folio-migration-tools.readthedocs.io/)\n\nA toolkit that enables you to migrate data over from a legacy ILS system into [FOLIO LSP](https://www.folio.org/)\n\n# What is it good for?\nFOLIO Migration tools enables you to migrate libraries with the most common ILS:s over to FOLIO without data losses or any major data transformation tasks. \nThe tools transforms and loads the data providing you and the library with good actionable logs and data cleaning task lists together with the migrated data.\n\n## What data does it cover?\nFOLIO Migration Tools currently covers the following data sets:\n* Catalog (Inventory and SRS in FOLIO terminology)\n* Circulation transactions (Open loans and requests)\n* Users/Patrons (In FOLIO, these share the same app/database)\n* Courses and Reserves (Course reserves)\n* Organizations (Vendor records)\n* Orders (limited support)\n\n### What additional functionality is on the roadmap?\nThis is the loose roadmap, in order of most likely implementations first\n* ERM-related objects\n* Financial records\n\n### Can I use the tools for ongoing imports and integrations?\nThe tools are primarliy maintained for performing initial data migrations. We recommend that you use native FOLIO functionality for ongoing loads where possible. \nIn theory, these tools can be used for ongoing patron loads from systems like Banner, Workday, or PeopleSoft. But we recommend you to weigh your options carefully before going down this path. \n\n# Contributing\nWant to contribute? Read the [CONTRIBUTING.MD](https://github.com/FOLIO-FSE/folio_migration_tools/blob/main/CONTRIBUTING.md)\n\n# Found an issue?\nReport it on the [Github Issue tracker](https://github.com/FOLIO-FSE/folio_migration_tools/issues)\n\nThe scripts requires a FOLIO tenant with reference data properly set up. The script will throw messages telling what reference data is missing.\n# Installing\nMake sure you are running Python 3.9 or above. \n## 1. Using pip and venv\n### 2.1. Create and activate a [virtual environment](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/#creating-a-virtual-environment)   \n```   \npython -m venv ./.venv     # Creates a virtual env in the current folder\nsource .venv/bin/activate  # Activates the venv    \n```\n### 2. Install using pip: \n```\npython -m pip install folio_migration_tools\n```\n### 3. Test the installation by showing the help pages \n```   \npython -m folio_migration_tools -h\n```    \n\n## 2. Using pipenv\n### 1. Run\n```   \npipenv install folio-migration-tools\n```   \n### 2. Test the installation by showing the help pages\n```  \npipenv run python3 -m folio_migration_tools -h\n```  \n\n# FOLIO migration process\nThis repo plays the main part in a process using a collection of tools. The process itself is documented in more detail, including example configuration files, at [this template repository](https://github.com/FOLIO-FSE/migration_repo_template)\nIn order to perform migrations according to this process, you need the following:\n* An Installation of [FOLIO Migration Tools](https://pypi.org/project/folio-migration-tools/). Installation instructions above.\n* A clone, or a separate repo created from [migration_repo_template](https://github.com/FOLIO-FSE/migration_repo_template)\n* Access to the [Data mapping file creator](https://data-mapping-file-creator.folio.ebsco.com/data_mapping_creation) web tool\n* A FOLIO tenant running the latest or the second latest version of FOLIO\n\n\n\n# Running the scripts\nFor information on syntax, what files are needed and produced by the toolkit, refer to the documentation and example files in the [template repository](https://github.com/FOLIO-FSE/migration_repo_template). We are building out the docs section in this repository as well:[Documentation](https://folio-migration-tools.readthedocs.io/en/latest/)\n¨\n',
    'author': 'Theodor Tolstoy',
    'author_email': 'github.teddes@tolstoy.se',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/FOLIO-FSE/folio_migration_tools',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
