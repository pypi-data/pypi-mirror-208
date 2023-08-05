# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

# Copyright 2022 Oxide Computer Company

class AuthenticationError(Exception):
  def __init__(self, message):
    super().__init__(message)

class BadRequestError(Exception):
  def __init__(self, message, errors):
    super().__init__(message, errors)

class ForbiddenError(Exception):
  def __init__(self, message):
    super().__init__(message)

class NotFoundError(Exception):
  def __init__(self, message):
    super().__init__(message)