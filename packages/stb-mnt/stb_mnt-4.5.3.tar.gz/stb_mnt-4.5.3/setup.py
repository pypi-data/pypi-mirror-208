# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['stb', 'stb.utils']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0',
 'keyring>=23.13.1,<24.0.0',
 'platformdirs>=2.6.2,<3.0.0',
 'pysh>=3.1.0,<4.0.0',
 'python-dotenv>=0.21.0,<0.22.0',
 'python-gitlab>=3.13.0,<4.0.0',
 'requests>=2.28.2,<3.0.0',
 'tomli>=2.0.1,<3.0.0',
 'tomlkit>=0.11.6,<0.12.0',
 'typer[all]>=0.6.1,<0.7.0',
 'typing-extensions>=4.3.0,<5.0.0']

entry_points = \
{'console_scripts': ['stb = stb:app']}

setup_kwargs = {
    'name': 'stb-mnt',
    'version': '4.5.3',
    'description': 'A universal tool for local microservice management.',
    'long_description': '# stb\n\nA universal tool for local microservice management\n\n## Requirements\n\n* [Poetry](https://python-poetry.org/) - Required for setup functionality \n* [Pyenv](https://github.com/pyenv/pyenv) - Optional\n\n## Installation\n\n```bash\npipx install stb-mnt\n```\n\n## Usage\n\n### Setup\n\n* To download and setup my_company/backend/service1 microservice as a subdirectory to the current working directory, use:\n\n```bash\nstb setup my_company/backend/service1\n```\n\n* To download and setup my_company/backend/service1 and my_company/backend/service2 as subdirectories to current working directory, use:\n\n```bash\nstb setup my_company/backend/service1 my_company/backend/service2\n```\n\n* To setup all backend services, use:\n\n```bash\nstb setup my_company/backend\n```\n\nNote that if you want to clone repositories, you must first set a `git_url` using `stb config set git_url` command\n\n### Update\n\n* To update .env file in accordance with .env.example in a microservice:\n\n```bash\nstb update env\n```\n\n* To synchronize service ports between all installed microservices (you can specify which ones will run locally with the `--local` option):\n\n```bash\nstb update ports\n```\n\n* To update poetry.lock file, install dependencies, stash current changes, checkout to master, pull from remote, and recreate databases:\n\n```bash\nstb update package -piucd\n```\n\nor  \n\n```bash\nstb update package --pull --update --checkout --reset-databases\n```\n\n### DB\n\n* To upgrade migrations in a microservice:\n\n```bash\nstb db upgrade\n```\n\n* To create databases and upgrade its migrations in a microservice:\n\n```bash\nstb db create\n```\n\n* To drop databases in a microservice:\n\n```bash\nstb db drop\n```\n\n* To drop and recreate databases, and upgrade migrations in a microservice:\n\n```bash\nstb db reset\n```\n\n* To upgrade migrations in parallel for faster upgrades (useful for large monoliths with multiple databases), you can use the -p (--parallel) option:\n\n```bash\nstb db create -p\n```\n  \n```bash\nstb db reset -p\n```\n  \n* To force dropping of databases in case another program is using them at the same time, you can use the -f (--force) option:\n\n```bash\nstb db drop -f\n```\n  \n```bash\nstb db reset -f\n```\n  \n### Use\n\n`stb use` allows you to take a company private package and install either a cloud version or a local version of it. STB will preserve all extras, automatically set package source, and will gracefully handle any issues that might happen while updating.\n\n* To install a local version of `my_package` that is located at `../my_package`:\n\n```bash\nstb use ../my_package\n```\n\n* To install a local version of `my_package` that is located at `../my_package` in editable mode:\n\n```bash\nstb use ../my_package --editable\n```\n\n* To install a cloud version of `my_package` with tag `8.3.1`:\n\n```bash\nstb use "my_package==8.3.1"\n```\n\n* To install a cloud version of my_package with tag `8.3.1`, my_other_package with any tag higher than `1.2.3`, and my_third_package with any tag more than or equal to `4.5.6` and less than `5.0.0`:\n\n```bash\nstb use "my_package==8.3.1" "my_other_package>1.2.3" "my_third_package^4.5.6"\n```\n\n### Run\n\n* To update and run the select services concurrently:\n\n```bash\nstb run service1 service2\n```\n\n### Config\n\n* To set a git url for cloning:\n\n```bash\nstb config set git_url git@gitlab.my_company.com\n```\n\n### Graph\n\n* To get a dependency graph of your microservices:\n\n```bash\nstb graph json my_company/backend/ my_company/infrastructure/\n```\n\n* To get a dependency graph of your microservices as an svg image (requires graphviz):\n\n```bash\nstb graph graphviz my_company/backend/ my_company/infrastructure/\n```\n\n### How directories are selected for update/db\n\nFor every update, you can specify:\n\n1) A microservice directory, which will cause stb to update only that microservice\n2) Several microservice directories, which will cause stb to update these microservices and integrate them together (for example, `update ports` assigns ports to local microservices and updates their links in other microservices to match the assigned ports)\n3) A directory with multiple microservice subdirectories inside it, which is equivalent to (2) with the list of subdirectories as arguments\n4) Nothing, which will choose the current working directory as the first argument and will be equivalent to (1) or (3)\n',
    'author': 'Stanislav Zmiev',
    'author_email': 'szmiev2000@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
