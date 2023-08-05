"""Models
------

Models for the django-e2ee-framework app.
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


from __future__ import annotations

# from typing import TYPE_CHECKING
from uuid import uuid4

from cryptography.hazmat.primitives import serialization
from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_logged_out
from django.contrib.sessions.models import Session
from django.core.exceptions import ValidationError
from django.db import models
from django.dispatch import receiver
from django.urls import reverse

from django_e2ee import app_settings  # noqa: F401


def validate_public_key(value: str):
    """Try importing a public key with cryptography"""
    try:
        serialization.load_pem_public_key(value.encode("utf-8"))
    except ValueError:
        raise ValidationError("Public key could not be imported.")


class MasterKey(models.Model):
    """A public key for a user that is used for encryption."""

    user = models.OneToOneField(
        get_user_model(),
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="master_key",
        help_text="The user that this key belongs to.",
    )

    pubkey = models.TextField(
        help_text="The exported public key.",
        max_length=1000,
        unique=True,
        validators=[validate_public_key],
    )

    signing_pubkey = models.TextField(
        help_text="The exported public key.",
        max_length=1000,
        unique=True,
        validators=[validate_public_key],
    )

    @property
    def pubkey_loaded(self):
        """The pubkey loaded via cryptography"""
        return serialization.load_pem_public_key(self.pubkey.encode("utf-8"))

    @property
    def signing_pubkey_loaded(self):
        """The pubkey loaded via cryptography"""
        return serialization.load_pem_public_key(
            self.signing_pubkey.encode("utf-8")
        )

    def __str__(self) -> str:
        return f"Master key of {self.user}"


class MasterKeySecret(models.Model):
    """The encrypted private key for a :class:`MasterKey`"""

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name="unique_master_key_identifier_for_user",
                fields=("identifier", "master_key"),
            )
        ]

    uuid = models.UUIDField(primary_key=True, default=uuid4)

    master_key = models.ForeignKey(MasterKey, on_delete=models.CASCADE)

    identifier = models.CharField(
        max_length=100, help_text="Identifier for this secret"
    )

    secret = models.TextField(
        help_text="The encrypted RSA-OAEP private key.", max_length=5000
    )

    signing_secret = models.TextField(
        help_text="The encrypted RSA-PSS private key.", max_length=5000
    )

    salt = models.CharField(
        max_length=50,
        help_text=(
            "The salt that has been used to generate the AES key that "
            "encrypted the :attr:`secret`. Only necessary if the AES key has "
            "been derived from a PBKDF2 key."
        ),
        null=True,
        blank=True,
    )

    iv = models.CharField(
        max_length=50, help_text="The vector data used when wrapping the key."
    )

    def __str__(self) -> str:
        return f"{self.identifier}"


class SessionKey(models.Model):
    """An encrypted private key for a :class:`MasterKey` for one  session."""

    session = models.OneToOneField(
        Session, primary_key=True, on_delete=models.CASCADE
    )

    session_secret = models.TextField(
        null=True,
        blank=True,
        help_text="The encrypted AES-GCM key of the session.",
        max_length=5000,
    )

    ignore = models.BooleanField(
        default=False,
        help_text="Ignore E2E for this session and do not ask again.",
    )

    secret = models.TextField(
        help_text="The encrypted RSA-OAEP private key of the user.",
        max_length=5000,
        null=True,
        blank=True,
    )

    signing_secret = models.TextField(
        help_text="The encrypted RSA-PSS private key of the user.",
        max_length=5000,
        null=True,
        blank=True,
    )

    iv = models.CharField(
        max_length=50,
        help_text="The vector data used when wrapping the private key.",
        null=True,
        blank=True,
    )

    master_key = models.ForeignKey(MasterKey, on_delete=models.CASCADE)

    def get_absolute_url(self):
        return reverse(
            "e2ee:sessionkey-detail", args=(self.session.session_key,)
        )

    def __str__(self) -> str:
        return (
            f"Session Key Secret of {self.master_key.user} for "
            f"{self.session.session_key}"
        )


class EncryptionKey(models.Model):
    """A key that is used for encrypting content in the database."""

    uuid = models.UUIDField(primary_key=True, default=uuid4)

    created_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="The user who created this key.",
    )

    master_keys = models.ManyToManyField(
        MasterKey,
        through="EncryptionKeySecret",
        blank=True,
        through_fields=("encryption_key", "encrypted_with"),
    )

    def __str__(self) -> str:
        return str(self.uuid)


class EncryptionKeySecret(models.Model):
    """The secret of an encryption key, encrypted with a users master key."""

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name="unique_encryption_key_for_user",
                fields=("encryption_key", "encrypted_with"),
            )
        ]

    encryption_key = models.ForeignKey(EncryptionKey, on_delete=models.CASCADE)

    encrypted_with = models.ForeignKey(
        MasterKey,
        on_delete=models.CASCADE,
        help_text="The master key that encrypted this secret.",
    )

    secret = models.TextField(
        help_text=(
            "The AES-Key of the encryption key, encrypted with the"
            " master key."
        ),
        max_length=5000,
    )

    signature = models.TextField(
        help_text=(
            "The signature of the secret signed by the user who created this."
        ),
        max_length=5000,
    )

    signed_by = models.ForeignKey(
        MasterKey,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="The master key that created and signed this secret.",
        related_name="signed_secrets",
    )

    def __str__(self) -> str:
        return (
            f"Secret of {self.encryption_key} for {self.encrypted_with.user}"
        )


@receiver(user_logged_out)
def delete_session_key(request, **kwargs):
    """Deactivate the notification subscriptions for the session."""
    SessionKey.objects.filter(session=request.session.session_key).delete()
