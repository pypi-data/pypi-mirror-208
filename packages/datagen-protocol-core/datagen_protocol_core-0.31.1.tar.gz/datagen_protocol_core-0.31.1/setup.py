# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['datagen_protocol',
 'datagen_protocol.migrations',
 'datagen_protocol.migrations.datapoint_migrations',
 'datagen_protocol.migrations.sequence_migrations',
 'datagen_protocol.schema',
 'datagen_protocol.schema.environment',
 'datagen_protocol.schema.hic',
 'datagen_protocol.schema.humans',
 'datagen_protocol.schema.humans.presets',
 'datagen_protocol.schema.humans.presets.expression_presets']

package_data = \
{'': ['*'], 'datagen_protocol': ['resources/*']}

install_requires = \
['dynaconf==2.2.3', 'pydantic']

setup_kwargs = {
    'name': 'datagen-protocol-core',
    'version': '0.31.1',
    'description': 'Datagen Protocol Core',
    'long_description': 'None',
    'author': 'ShayZ',
    'author_email': 'shay.zilberman@datagen.tech',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
