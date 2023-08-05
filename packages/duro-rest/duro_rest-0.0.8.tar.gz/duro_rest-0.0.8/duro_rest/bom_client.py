# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

# Copyright 2022 Oxide Computer Company

import copy
import json
from duro_rest.duro_client import Client, Cache

class FlattenedBOM(list):
  def __init__(self, data: list):
    list.__init__(self, data)
    self.__data = data

  def __eq__(self, other):
    if isinstance(other, FlattenedBOM):
        return self.__data == other.inner()

    return False

  def inner(self) -> list:
    return self.__data

class IndentedBOM(list):
  def __init__(self, data: list):
    list.__init__(self, data)
    self.__data = data

  def __eq__(self, other):
    if isinstance(other, IndentedBOM):
        return self.__data == other.inner()

    return False

  def inner(self) -> list:
    return self.__data

  def flattened(self) -> FlattenedBOM:
    source = copy.deepcopy(self.__data)

    # Create a list to hold the unique components in the BOM
    unique_components = []

    # Keys that are allowed to differ between components. We will either reconcile these values (as
    # we do in the case of quantity and refDes) or we may drop / ignore the value (as we do in the
    # case of itemNumber)
    allowed_conflicts = [
      'quantity',                 # Sum
      'refDes'                    # Concat
    ]

    for component in source:
      # For a flattened BOM we are only interested in the multiplied quantities
      component['quantity'] = component['multiplied_quantity']

      # We need to drop a few fields that we are not interested in, or can not merge
      component.pop('isAddedAfterPullRequest', None)
      component.pop('itemNumber', None)
      component.pop('multiplied_quantity', None)
      component.pop('parents', None)
      component.pop('parent_cpns', None)
      component.pop('level', None)

      # For each component, check the id to see if we already have it in the list of unique
      # components
      existing = next((c for c in unique_components if component['_id'] == c['_id']), None)

      # If we found an existing component, sum together the quantities of the current component and
      # the existing component
      if existing:

        # Check that the two components differ at most in terms of quantity
        for k, v in component.items():
          assert k in allowed_conflicts or existing[k] == v, "Values for key `" + k + "` do not match. Unable to merge components. Existing (" + str(existing[k]) + ") != Current (" + str(v) + ")"

        existing['quantity'] = existing['quantity'] + component['quantity']

        if 'refDes' in component and component['refDes'] != '':
          existing['refDes'] = existing['refDes'] + ',' + component['refDes']
      else:
        # Otherwise this is a component we have not seen yet. Just add it to the list
        unique_components.append(component)

    return FlattenedBOM(unique_components)

class NestedBOM(dict):
  def __init__(self, data: dict):
    # Assign a default quantity of 1 to the top line item if it has not yet been assigned a quantity
    if not 'quantity' in data:
      data['quantity'] = 1

    dict.__init__(self, data)
    self.__data = data

  def __eq__(self, other):
    if isinstance(other, NestedBOM):
        return self.__data == other.inner()

    return False

  def inner(self) -> dict:
    return self.__data

  def indented(self) -> IndentedBOM:
    source = copy.deepcopy(self.__data)

    # We need to first take the nested BOM and transform it into a flat list of components. The
    # quantity for a given component is multiplied by each of its parents quantity. This list will
    # contain duplicate components which will need to be deduplicated when transforming to a
    # flattened BOM
    components = component_list(source)

    return IndentedBOM(components)

def component_list(component) -> list:
  # When we start processing a component, set its multiplied quantity to its non-multiplied
  # quantity. As we traverse back up the tree this field will be updated as needed
  component['multiplied_quantity'] = component['quantity']

  # Start an empty lit of parent component ids
  component['parents'] = []
  component['parent_cpns'] = []

  # Component depth starts at 0 and will be incremented as we walk back up the tree
  component['level'] = 0

  # The component passed in represents a portion of the nested BOM. Here we are going to flatten all
  # of this component's children (and nested children) by calling component_list on each child
  # component. Since component_list returns a list of components, the map call here will end up
  # with a list of lists. Therefore we call flatten to turn that result from a list of lists into
  # a list of components
  flattened_children = flatten(map(component_list, component['children']))

  for child in flattened_children:
    # For each child component we multiply its quantity by the quantity of the current component
    # we are looking at. We store the value to make future work easier
    child['multiplied_quantity'] = component['multiplied_quantity'] * child['multiplied_quantity']

    # We also want to track the parents list to identify the path back up the tree from a leaf
    child['parents'].append(component['_id'])
    child['parent_cpns'].append(component['cpn'])

    # Increment the level of each child component by one
    child['level'] = child['level'] + 1

  # Since we are flattening the BOM we no longer want the components to have references to their
  # children
  component.pop('children', None)

  # Finally return a flattened list that contains the current component and all of its children
  return [component] + flattened_children

class BOMClient(Client):
  def __init__(self, api_key, url = "https://public-api.duro.app", cache = Cache(0)):
    super().__init__(api_key, url, cache)

  def product_bom(self, id) -> NestedBOM:
    return self.__nested_bom(self.product(id))

  def component_bom(self, id) -> NestedBOM:
    return self.__nested_bom(self.component(id))

  def __nested_bom(self, parent) -> NestedBOM:
    components = self.components()

    # We we request a product or component from Duro the 'children' property only contains a single
    # level of depth. What we need is the full nested BOM. We call expand_child_components on each
    # child to build out that full tree.
    parent['children'] = list(map(lambda child: expand_child_components(child, components), parent['children']))

    return NestedBOM(parent)

def expand_child_components(child, components):
  # The components list contains most of the needed data, but we need some of the properties that
  # are defined by the child component (specifically the quantity). Therefore we combine the
  # properties of the child we are currently expanding with the expanded data available from
  # fetching all of the components
  matching_components = list(component for component in components if component['_id'] == child['component'])

  if len(matching_components) == 0:
    raise LookupError('Failed to find component in cache ' + child['component'])
  elif len(matching_components) > 1:
    raise LookupError('Found multiple components in cache ' + child['component'])

  expanded_child = {**child, **matching_components[0]}

  # Now that we have expanded the child component, we need to expand each of its child components
  expanded_child['children'] = list(map(lambda child: expand_child_components(child, components), expanded_child['children']))

  return expanded_child

def flatten(l):
  return [item for sublist in l for item in sublist]