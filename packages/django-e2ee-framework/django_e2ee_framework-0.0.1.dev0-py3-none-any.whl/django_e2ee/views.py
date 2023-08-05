"""Views
-----

Views of the django-e2ee-framework app to be imported via the url
config (see :mod:`django_e2ee.urls`).
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

from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, viewsets

from django_e2ee import app_settings  # noqa: F401
from django_e2ee import models, serializers
from django_e2ee.context_processors import get_e2ee_login_context_data
from django_e2ee.permissions import HasEncryptionSecretPermission


def dummy_view(request, *args, **kwargs):
    raise Http404


class E2ELoginViewMixin:
    """A mixin that gets a form to login or create an E2EE password.

    This mixin provides an additional ``e2ee_login_form`` context variable for the
    template. Depending on the fact whether the user already created an E2EE
    password, this can be a :class:`django_e2ee.forms.PasswordCreateForm`
    to create a new E2EE password, or a
    :class:`django_e2ee.forms.PasswordInputForm` to enter the password.

    Additionally, it adds a context variable ``e2ee_login_url`` that points
    to the URL where the form should be submitted.
    """

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_e2ee_login_context_data(self.request))
        return context


class MasterKeyViewSet(viewsets.ModelViewSet):
    """A view to create and retrieve a users :model:`e2ee.MasterKey`"""

    permission_classes = [
        permissions.IsAuthenticated,
        permissions.DjangoModelPermissions,
    ]

    serializer_class = serializers.MasterKeySerializer

    queryset = models.MasterKey.objects.all()


class MasterKeySecretViewSet(viewsets.ModelViewSet):
    """A viewset for a users :model:`e2ee.MasterKeySecret`"""

    permission_classes = [permissions.IsAuthenticated]

    serializer_class = serializers.MasterKeySecretSerializer

    queryset = models.MasterKeySecret.objects.all()

    def get_queryset(self):
        qs = super().get_queryset()
        try:
            master_key = self.request.user.master_key
        except AttributeError:
            return qs.none()
        else:
            return qs.filter(master_key=master_key)


class SessionKeyViewSet(viewsets.ModelViewSet):
    """A viewset for a users :model:`e2ee.SessionKey`"""

    permission_classes = [permissions.IsAuthenticated]

    serializer_class = serializers.SessionKeySerializer

    queryset = models.SessionKey.objects.all()

    def get_queryset(self):
        qs = super().get_queryset()
        try:
            master_key = self.request.user.master_key
        except AttributeError:
            return qs.none()
        else:
            return qs.filter(master_key=master_key)


class EncryptionKeyViewSet(viewsets.ModelViewSet):
    """A viewset for :model:`e2ee.EncryptionKey`"""

    permission_classes = [permissions.IsAuthenticated]

    serializer_class = serializers.EncryptionKeySerializer

    queryset = models.EncryptionKey.objects.all()

    def get_queryset(self):
        qs = super().get_queryset()
        try:
            master_key = self.request.user.master_key
        except AttributeError:
            return qs.filter(created_by=self.request.user)
        else:
            return qs.filter(
                Q(created_by=self.request.user) | Q(master_keys=master_key)
            )


class MasterKeyRetrieveView(generics.RetrieveAPIView):
    """Retreive the master key of the user."""

    permission_classes = [permissions.IsAuthenticated]

    serializer_class = serializers.MasterKeySerializer

    def get_object(self):
        try:
            master_key = self.request.user.master_key
        except AttributeError:
            raise Http404(f"{self.request.user} does not have a master key")
        else:
            return master_key


class SessionKeyUpdateView(generics.RetrieveAPIView, generics.UpdateAPIView):
    """Retreive the master key of the user."""

    permission_classes = [permissions.IsAuthenticated]

    serializer_class = serializers.SessionKeySerializer

    def get_object(self):
        try:
            master_key = self.request.user.master_key
        except AttributeError:
            raise Http404(f"{self.request.user} does not have a master key")
        else:
            return get_object_or_404(
                models.SessionKey,
                master_key=master_key,
                session__session_key=self.request.session.session_key,
            )


class EncryptionKeySecretView(
    generics.RetrieveAPIView, generics.CreateAPIView
):
    """A view to create and get :model:`e2ee.EncryptionKeySecret`."""

    permission_classes = [
        permissions.IsAuthenticated,
        HasEncryptionSecretPermission,
    ]

    serializer_class = serializers.EncryptionKeySecretSerializer

    queryset = models.EncryptionKeySecret.objects.all()

    def get_object(self):
        qs = self.get_queryset()
        try:
            master_key = self.request.user.master_key
        except AttributeError:
            raise Http404(f"{self.request.user} does not have a master key")
        else:
            return get_object_or_404(qs, encrypted_with=master_key)

    def get_serializer(self, *args, **kwargs):
        if isinstance(kwargs.get("data", {}), list):
            kwargs["many"] = True
        return super().get_serializer(*args, **kwargs)

    def get_queryset(self):
        try:
            master_key = self.request.user.master_key
        except AttributeError:
            return super().get_queryset().none()
        else:
            encryption_key = get_object_or_404(
                models.EncryptionKey, pk=self.kwargs["pk"]
            )
            if not (
                encryption_key.created_by.pk == self.request.user.pk
                or encryption_key.master_keys.filter(pk=master_key.pk)
            ):
                raise Http404(
                    f"{self.request.user} has no access to this key."
                )
            return encryption_key.encryptionkeysecret_set.all()
