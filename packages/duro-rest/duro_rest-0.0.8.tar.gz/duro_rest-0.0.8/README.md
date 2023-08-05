# duro_rest

An API client for the [Duro REST API](https://public-api.duro.app/v1/docs/).

## Installation

Installing from [PyPi]()

```pip install duro_rest```

Installing from [conda-forge]()

TBD

## Examples

The Duro client is a very minimal API client for reading data from the [Duro v1 REST API](https://public-api.duro.app/v1/docs/). It does not define classes for each object type and instead returns plain dictionaries
and lists.

#### Base Client

```python
from duro_rest import Client

# Create a new client, providing your API key. By default clients will make calls to the public REST
# API, but the endpoint base can be overridden if needed
client = Client("your-api-key")

# Fetch a component by its Duro assigned id (as opposed to the CPN)
component = client.component("component-id")

# Fetch a list of all components in Duro
components = client.components()

# Fetch a list of all components in Duro filtered by status
components = client.components(status = "OBSOLETE")
```

#### BOM Client

The Duro API does not support pulling BOMs directly. The BOM Client is here to make that experience
a little easier.

```python
from duro_rest import BOMClient

# Create a new bom client for fetching full BOMs (either nested or flattened). It accepts the same
# arguments as the base client
client = Client("your-api-key")

# Get a nested BOM starting from a product
nested_product_bom = client.product_bom("product-id")

# Get a nested BOM starting from a component
nested_component_bom = client.component("component-id")

# Convert the nested BOM into flattened BOM
indented_product_bom = nested_product_bom.idented()

# Flattening will collapse rows for the same components together
flattened_product_bom = indented_product_bom.flatten()
```