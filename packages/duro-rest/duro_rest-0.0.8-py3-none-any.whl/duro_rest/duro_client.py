# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

# Copyright 2022 Oxide Computer Company

import copy
from datetime import datetime, timedelta
import json
from json import JSONDecodeError
import math
import requests

from duro_rest.error import AuthenticationError, BadRequestError, ForbiddenError, NotFoundError

class Cache():
  def __init__(self, cache_duration):
    self.__delta = timedelta(seconds = cache_duration)
    self.__data = {}

  def get(self, key):
    if key in self.__data:
      (value, expiration) = self.__data[key]

      if datetime.now().timestamp() < expiration:
        return copy.deepcopy(value)

    return None

  def insert(self, key, value):
    if self.__delta.seconds > 0:
      self.__data[key] = (value, (datetime.now() + self.__delta).timestamp())

class FileCache(Cache):
  def __init__(self, cache_duration, path):
    super().__init__(cache_duration)

    try:
      self.__cache_file = open(path, "r+")
      stored = json.load(self.__cache_file)

      if stored != None:
        self._Cache__data = stored
    except TypeError:
      # Ignore
      pass
    except JSONDecodeError:
      # Ignore
      pass
    except FileNotFoundError:
      self.__cache_file = open(path, "w")
      pass
    finally:
      # Make sure we always rewind to the start of the file
      self.__cache_file.seek(0, 0)

  def save(self):
    self.__cache_file.truncate()
    self.__cache_file.write(json.dumps(self._Cache__data))
    self.__cache_file.seek(0, 0)

class Client:
  def __init__(self, api_key, url = "https://public-api.duro.app", cache = Cache(0)):
    self.__base_url = url + "/v1/"
    self.__api_key = api_key
    self.__cache = cache

  def categories(
    self,
    name = None,
    type_ = None,
    prefix = None
  ):
    return self.__get_paginated(
      "categories",
      "categories",
      {
        "name": name,
        "type": type_,
        "prefix": prefix
      }
    )

  def change_order(self, id):
    return self.__get("changeorders/" + id)

  def change_orders(
    self,
    con = None,
    name = None,
    status = None,
    resolution = None
  ):
    return self.__get_paginated(
      "changeorders",
      "changeOrders",
      {
        "con": con,
        "name": name,
        "status": status,
        "resolution": resolution
      }
    )

  def component(self, id):

    # Try to serve from the cache
    if entries := self.__cache.get("components"):
      for entry in entries:
        if entry["_id"] == id:
          return entry

    return self.__get("components/" + id)

  def components(
    self,
    mass = None,
    modified = None,
    cpn = None,
    name = None,
    eid = None,
    revision = None,
    category = None,
    cat_group = None,
    status = None,
    document_name = None,
    document_mime_type = None,
    document_revision = None,
    document_status = None,
    document_type = None,
    procurement = None
  ):
    return self.__get_paginated(
      "components",
      "components",
      {
        "mass": mass,
        "modified": modified,
        "cpn": cpn,
        "name": name,
        "eid": eid,
        "revision": revision,
        "category": category,
        "catGroup": cat_group,
        "status": status,
        "documentName": document_name,
        "documentMimeType": document_mime_type,
        "documentRevision": document_revision,
        "documentStatus": document_status,
        "documentType": document_type,
        "procurement": procurement
      }
    )

  def component_revision(self, id):
    return self.__get("component/revision/" + id)

  def component_revisions(
    self,
    mass = None,
    modified = None,
    cpn = None,
    name = None,
    eid = None,
    revision = None,
    category = None,
    cat_group = None,
    status = None,
    document_name = None,
    document_mime_type = None,
    document_revision = None,
    document_status = None,
    document_type = None,
    procurement = None
  ):
    return self.__get_paginated(
      "component/revision",
      "componentRevisions",
      {
        "mass": mass,
        "modified": modified,
        "cpn": cpn,
        "name": name,
        "eid": eid,
        "revision": revision,
        "category": category,
        "catGroup": cat_group,
        "status": status,
        "documentName": document_name,
        "documentMimeType": document_mime_type,
        "documentRevision": document_revision,
        "documentStatus": document_status,
        "documentType": document_type,
        "procurement": procurement
      }
    )

  def document(self, id):
    return self.__get("documents/" + id)

  def product(self, id):
    return self.__get("products/" + id)

  def products(
    self,
    mass = None,
    modified = None,
    cpn = None,
    name = None,
    eid = None,
    revision = None,
    status = None,
    document_name = None,
    document_mime_type = None,
    document_revision = None,
    document_status = None,
    document_type = None,
    procurement = None
  ):
    return self.__get_paginated(
      "products",
      "products",
      {
        "mass": mass,
        "modified": modified,
        "cpn": cpn,
        "name": name,
        "eid": eid,
        "revision": revision,
        "status": status,
        "documentName": document_name,
        "documentMimeType": document_mime_type,
        "documentRevision": document_revision,
        "documentStatus": document_status,
        "documentType": document_type,
        "procurement": procurement
      }
    )

  def product_revision(self, id):
    return self.__get("product/revision/" + id)

  def product_revisions(
    self,
    mass = None,
    modified = None,
    cpn = None,
    name = None,
    eid = None,
    revision = None,
    status = None,
    document_name = None,
    document_mime_type = None,
    document_revision = None,
    document_status = None,
    document_type = None,
    procurement = None
  ):
    return self.__get_paginated(
      "product/revision",
      "productRevisions",
      {
        "mass": mass,
        "modified": modified,
        "cpn": cpn,
        "name": name,
        "eid": eid,
        "revision": revision,
        "status": status,
        "documentName": document_name,
        "documentMimeType": document_mime_type,
        "documentRevision": document_revision,
        "documentStatus": document_status,
        "documentType": document_type,
        "procurement": procurement
      }
    )

  def user(self, id):
    return self.__get("users/" + id)

  def users(
    self,
    email = None,
    role = None
  ):
    return self.__get_paginated(
      "users",
      "users",
      {
        "email": email,
        "role": role
      }
    )

  def __get_paginated(self, path, resultKey, params):
    resources = []

    page = self.__get(path, params = {"perPage": 100, **params})

    total_results = page["resultCount"]
    pages = math.ceil(total_results / 100)

    resources = resources + page[resultKey]

    if pages > 1:
      for page_index in range(2, pages + 1):
        page = self.__get(path, params = {**params, "perPage": 100, "page": page_index})
        resources = resources + page[resultKey]

    # For each resource we found populate its individual record in the cache
    for resource in resources:
      self.__cache.insert(path + "/" + resource["_id"] + "::{}", resource)

    return resources

  def __get(self, path, headers = {}, params = {}, data = None):
    cache_key = path + "::" + json.dumps(params)

    if (value := self.__cache.get(cache_key)) is not None:
      return value

    headers["x-api-key"] = self.__api_key

    resp = requests.get(self.__base_url + path, headers = headers, params = params, data = data)

    if resp.status_code == 400:
      raise BadRequestError(resp.json()["message"], resp.json()["errors"])
    if resp.status_code == 401:
      raise AuthenticationError(resp.json()["message"])
    if resp.status_code == 403:
      raise ForbiddenError(resp.json()["message"])
    if resp.status_code == 404:
      raise NotFoundError(resp.json()["message"])
    else:
      data = resp.json()
      self.__cache.insert(cache_key, data)
      return self.__cache.get(cache_key)