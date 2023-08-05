"""Serializers
-----------

Serializers for the django-e2ee-framework app.
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


from django.contrib.sessions.models import Session
from django.db import IntegrityError
from rest_framework import fields, serializers

from django_e2ee import models


class MasterKeySerializer(serializers.ModelSerializer):
    """A serialializer for :model:`e2ee.MasterKey`."""

    class Meta:
        model = models.MasterKey
        fields = ["pubkey", "signing_pubkey", "user"]
        read_only_fields = ["user"]

    def create(self, validated_data):
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            validated_data["user"] = request.user
        return super().create(validated_data)


class MasterKeySecretSerializer(serializers.ModelSerializer):
    """A serialializer for :model:`e2ee.MasterKeySecret`."""

    class Meta:
        model = models.MasterKeySecret
        fields = [
            "identifier",
            "secret",
            "signing_secret",
            "salt",
            "iv",
            "uuid",
        ]

    def create(self, validated_data):
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            validated_data["master_key"] = request.user.master_key
        return super().create(validated_data)


class SessionKeySerializer(serializers.ModelSerializer):
    """A serialializer for :model:`e2ee.SessionKey`."""

    class Meta:
        model = models.SessionKey
        fields = [
            "session",
            "session_secret",
            "secret",
            "signing_secret",
            "iv",
            "ignore",
        ]
        read_only_fields = ["session"]

    def create(self, validated_data):
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            validated_data["master_key"] = request.user.master_key
        if request and hasattr(request, "session"):
            validated_data["session"] = Session.objects.get(
                session_key=request.session.session_key
            )
        return super().create(validated_data)


class EncryptionKeySerializer(serializers.ModelSerializer):
    """A serialializer for :model:`e2ee.EncryptionKey`."""

    class Meta:
        model = models.EncryptionKey
        fields = ["uuid"]

    def create(self, validated_data):
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            validated_data["created_by"] = request.user
        return super().create(validated_data)


class BulkCreateListSerializer(serializers.ListSerializer):
    def create(self, validated_data):
        result = []
        for attrs in validated_data:
            try:
                result.append(self.child.create(attrs))
            except IntegrityError:
                pass

        return result


class EncryptionKeySecretSerializer(serializers.ModelSerializer):
    """A serialializer for :model:`e2ee.EncryptionKeySecret`."""

    class Meta:
        model = models.EncryptionKeySecret
        fields = [
            "encryption_key",
            "encrypted_with",
            "secret",
            "signature",
            "signed_by",
        ]
        read_only_fields = ["encryption_key", "signed_by"]

        list_serializer_class = BulkCreateListSerializer

    def create(self, validated_data):
        request = self.context.get("request")
        view = self.context.get("view")
        if request and hasattr(request, "user"):
            validated_data["signed_by"] = request.user.master_key
        if view and "pk" in view.kwargs:
            key = models.EncryptionKey.objects.get(pk=view.kwargs["pk"])
            validated_data["encryption_key"] = key
        validated_data["encrypted_with"] = models.MasterKey.objects.get(
            pubkey=validated_data["encrypted_with"]["pubkey"]
        )
        return super().create(validated_data)

    signed_by = serializers.PrimaryKeyRelatedField(read_only=True)
    encrypted_with = fields.CharField(source="encrypted_with.pubkey")
