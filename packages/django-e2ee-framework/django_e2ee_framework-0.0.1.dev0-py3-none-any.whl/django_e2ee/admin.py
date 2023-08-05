"""Admin interfaces
----------------

This module defines the django-e2ee-framework
Admin interfaces.
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


from django.contrib import admin  # noqa: F401

from django_e2ee import models  # noqa: F401


class MasterKeySecretInline(admin.StackedInline):
    """An inline for master key secrets."""

    model = models.MasterKeySecret

    readonly_fields = ["uuid", "secret", "signing_secret", "salt", "iv"]

    extra = 0

    def has_add_permission(self, request, obj) -> bool:  # type: ignore
        return False


class SessionKeyInline(admin.StackedInline):
    """An inline for session keys."""

    model = models.SessionKey

    readonly_fields = ["session_secret", "secret", "signing_secret", "iv"]

    exclude = ["session"]

    extra = 0

    def has_add_permission(self, request, obj) -> bool:  # type: ignore
        return False


@admin.register(models.MasterKey)
class MasterKeyAdmin(admin.ModelAdmin):
    """An admin for a master key"""

    readonly_fields = ["pubkey", "signing_pubkey"]

    list_display = ["user"]

    inlines = [MasterKeySecretInline, SessionKeyInline]

    def has_add_permission(self, request) -> bool:
        return False


class EncryptionKeySecretInline(admin.StackedInline):
    """An inline for an encryption key secret."""

    model = models.EncryptionKeySecret

    readonly_fields = ["encrypted_with", "secret", "signature", "signed_by"]

    extra = 0

    def has_add_permission(self, request, obj) -> bool:  # type: ignore
        return False


@admin.register(models.EncryptionKey)
class EncryptionKeyAdmin(admin.ModelAdmin):
    """An admin for encryption keys."""

    list_display = ["uuid", "created_by"]

    inlines = [EncryptionKeySecretInline]

    def has_add_permission(self, request) -> bool:
        return False
