# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['latch_postgres']

package_data = \
{'': ['*']}

install_requires = \
['latch-config>=0.1.6,<0.2.0',
 'latch-data-validation>=0.1.3,<0.2.0',
 'latch-o11y>=0.1.4,<0.2.0',
 'opentelemetry-api>=1.15.0,<2.0.0',
 'opentelemetry-sdk>=1.15.0,<2.0.0',
 'psycopg[binary,pool]>=3.1.8,<4.0.0',
 'typing-extensions>=4.4.0,<5.0.0']

setup_kwargs = {
    'name': 'latch-postgres',
    'version': '0.1.7',
    'description': 'Postges wrapper for latch python backend services',
    'long_description': '# python-postgres\n',
    'author': 'Max Smolin',
    'author_email': 'max@latch.bio',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.11,<4.0',
}


setup(**setup_kwargs)
