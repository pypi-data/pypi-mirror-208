"""Permissions
-----------

Custom permissions for the restAPI.
"""

# Disclaimer
# ----------
#
# Copyright (C) 2022 Helmholtz-Zentrum Hereon
#
# This file is part of django-e2ee-framework and is released under the
# EUPL-1.2 license.
# See LICENSE in the root of the repository for full licensing details.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the EUROPEAN UNION PUBLIC LICENCE v. 1.2 or later
# as published by the European Commission.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# EUPL-1.2 license for more details.
#
# You should have received a copy of the EUPL-1.2 license along with this
# program. If not, see https://www.eupl.eu/.

from rest_framework.permissions import BasePermission


class HasEncryptionSecretPermission(BasePermission):
    """Check if the user has access to the :model:`e2ee.EncryptionKey`."""

    def has_object_permission(self, request, view, obj):
        return (
            hasattr(request.user, "master_key")
            and request.user.master_key.pk == obj.encrypted_with.pk
        )
