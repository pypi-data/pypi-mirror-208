# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['duro_rest']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2,<3']

setup_kwargs = {
    'name': 'duro-rest',
    'version': '0.0.8',
    'description': 'An API client for the Duro REST API',
    'long_description': '# duro_rest\n\nAn API client for the [Duro REST API](https://public-api.duro.app/v1/docs/).\n\n## Installation\n\nInstalling from [PyPi]()\n\n```pip install duro_rest```\n\nInstalling from [conda-forge]()\n\nTBD\n\n## Examples\n\nThe Duro client is a very minimal API client for reading data from the [Duro v1 REST API](https://public-api.duro.app/v1/docs/). It does not define classes for each object type and instead returns plain dictionaries\nand lists.\n\n#### Base Client\n\n```python\nfrom duro_rest import Client\n\n# Create a new client, providing your API key. By default clients will make calls to the public REST\n# API, but the endpoint base can be overridden if needed\nclient = Client("your-api-key")\n\n# Fetch a component by its Duro assigned id (as opposed to the CPN)\ncomponent = client.component("component-id")\n\n# Fetch a list of all components in Duro\ncomponents = client.components()\n\n# Fetch a list of all components in Duro filtered by status\ncomponents = client.components(status = "OBSOLETE")\n```\n\n#### BOM Client\n\nThe Duro API does not support pulling BOMs directly. The BOM Client is here to make that experience\na little easier.\n\n```python\nfrom duro_rest import BOMClient\n\n# Create a new bom client for fetching full BOMs (either nested or flattened). It accepts the same\n# arguments as the base client\nclient = Client("your-api-key")\n\n# Get a nested BOM starting from a product\nnested_product_bom = client.product_bom("product-id")\n\n# Get a nested BOM starting from a component\nnested_component_bom = client.component("component-id")\n\n# Convert the nested BOM into flattened BOM\nindented_product_bom = nested_product_bom.idented()\n\n# Flattening will collapse rows for the same components together\nflattened_product_bom = indented_product_bom.flatten()\n```',
    'author': 'Augustus Mayo',
    'author_email': 'augustus@oxidecomputer.com',
    'maintainer': 'Augustus Mayo',
    'maintainer_email': 'augustus@oxidecomputer.com',
    'url': 'https://pypi.org/project/duro-rest/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
