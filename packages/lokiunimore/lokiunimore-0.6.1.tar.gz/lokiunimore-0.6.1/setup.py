# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['lokiunimore',
 'lokiunimore.config',
 'lokiunimore.matrix',
 'lokiunimore.matrix.templates',
 'lokiunimore.sql',
 'lokiunimore.utils',
 'lokiunimore.web',
 'lokiunimore.web.extensions']

package_data = \
{'': ['*'],
 'lokiunimore.web': ['static/*',
                     'templates/*',
                     'templates/errors/*',
                     'templates/matrix/*']}

install_requires = \
['Authlib>=1.0.1,<2.0.0',
 'Flask-SQLAlchemy>=2.5.1,<3.0.0',
 'Flask>=2.2.2,<3.0.0',
 'cfig[cli]>=0.3.0,<0.4.0',
 'coloredlogs>=15.0.1,<16.0.0',
 'gunicorn>=20.1.0,<21.0.0',
 'matrix-nio>=0.20.1,<0.21.0',
 'psycopg2>=2.9.3,<3.0.0',
 'python-dotenv>=0.21.0,<0.22.0',
 'requests>=2.28.1,<3.0.0']

entry_points = \
{'console_scripts': ['lokiunimore = lokiunimore.__main__:main']}

setup_kwargs = {
    'name': 'lokiunimore',
    'version': '0.6.1',
    'description': 'Matrix room gatekeeper bot for the unofficial Unimore space',
    'long_description': "# Loki Bot\n\nGatekeeper bot for the Unimore Informatica unofficial Matrix space\n\n\\[ [**Website**](https://loki.steffo.eu) | [PyPI](https://pypi.org/project/lokiunimore/) \\]\n\n> TIP: You may be looking for its predecessor, [Thor Bot](https://github.com/Steffo99/thorunimore).\n\n![](lokiunimore/web/static/opengraph.png)\n\n## Functionality\n\nThis bot monitors a [pre-configured *public* Matrix space][config-public-space] for join events, sending a [welcome message][welcome-msg] to every new joiner.\n\nThe [welcome message][welcome-msg] contains a link, which when clicked starts the user verification process:\n\n1. a page describing the bot is opened, and it allows users to login with a [pre-configured OpenID Connect Identity Provider][config-oidc-idp];\n2. the claims of the OIDC IdP are verified, and the user's email address is checked to verify that its domain matches a [pre-configured RegEx][config-email-regex]\n with specific email requirements;\n3. if the email address fullfils all the requirements, an invitation to a different, [pre-configured *private* Matrix space][config-private-space] is sent to the user.\n\nAdditionally, the bot monitors for leave events from both spaces, deleting user data if no longer needed to protect the user's privacy.\n\n[welcome-msg]: https://github.com/Steffo99/lokiunimore/blob/99f7101abc3f68472844cd2f1bac5119e41c1682/lokiunimore/matrix/templates/messages.py#L3-L23\n[config-public-space]: https://github.com/Steffo99/lokiunimore/blob/main/lokiunimore/config/config.py#L50-L60\n[config-oidc-idp]: https://github.com/Steffo99/lokiunimore/blob/main/lokiunimore/config/config.py#L147-L202\n[config-email-regex]: https://github.com/Steffo99/lokiunimore/blob/main/lokiunimore/config/config.py#L194-L202\n[config-private-space]: https://github.com/Steffo99/lokiunimore/blob/99f7101abc3f68472844cd2f1bac5119e41c1682/lokiunimore/config/config.py#L76-L86\n\n## Setting up a development environment\n\n### Dependencies\n\nThis project uses [Poetry](https://python-poetry.org/) to manage the dependencies.\n\nTo install all dependencies in a venv, run:\n\n```console\n$ poetry install\n```\n\n> TIP: For easier venv management, you may want to set:\n> \n> ```console\n> $ poetry config virtualenvs.in-project true\n> ```\n\nTo activate the venv, run:\n\n```console\n$ poetry shell\n```\n\nTo run something in the venv without activating it, run:\n\n```console\n$ poetry run <COMMAND>\n```\n\n### Environment\n\nLoki requires a lot of environment variables to be set, therefore it makes use of [cfig](https://cfig.readthedocs.io/en/latest/) to simplify the setup.\n\nTo view the current configuration, followed by a description of each variable, run:\n\n```console\n$ poetry run python -m lokiunimore.config\n```\n\n## Deploying in production\n\nUse the [pre-built Docker image](https://github.com/Steffo99/lokiunimore/pkgs/container/lokiunimore), or build it from the [provided Dockerfile](Dockerfile).\n\nRun the image without any command to view and validate the current configuration.\n\nRun the image with the `gunicorn -b 0.0.0.0:80 lokiunimore.web.app:rp_app` command to launch the production web server on local port 80, expecting to be behind a  reverse proxy.\n\nRun the image with the `lokiunimore.matrix` command to launch the Matrix bot.\n\n### Using Docker Compose\n\nUse the [given Docker Compose file](docker-compose.yml).\n\nEither use [Portainer](https://www.portainer.io/), or start it manually using `docker compose up -d && docker compose logs -f`.\n",
    'author': 'Stefano Pigozzi',
    'author_email': 'me@steffo.eu',
    'maintainer': 'Stefano Pigozzi',
    'maintainer_email': 'me@steffo.eu',
    'url': 'https://loki.steffo.eu/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
