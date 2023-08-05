# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['compose',
 'compose.command',
 'compose.dependency',
 'compose.event',
 'compose.query',
 'compose.query.mongo',
 'compose.query.mongo.op',
 'compose.query.mongo.op.aggregation',
 'compose.repository',
 'compose.schema',
 'compose.types']

package_data = \
{'': ['*']}

install_requires = \
['dependency-injector>=4.41.0,<5.0.0',
 'inflection>=0.5.1,<0.6.0',
 'pendulum>=2.1.2,<3.0.0',
 'pydantic>=1.10.2,<2.0.0',
 'pymongo[aws]>=4.3.3,<5.0.0']

setup_kwargs = {
    'name': 'pozalabs-compose',
    'version': '0.13.0',
    'description': 'Backend components for POZAlabs',
    'long_description': 'None',
    'author': 'sunwoong',
    'author_email': 'sunwoong@pozalabs.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
