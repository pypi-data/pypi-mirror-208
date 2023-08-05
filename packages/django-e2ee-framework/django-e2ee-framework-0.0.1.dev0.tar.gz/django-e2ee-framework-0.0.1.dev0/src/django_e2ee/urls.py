"""URL config
----------

URL patterns of the django-e2ee-framework to be included via::

    from django.urls import include, path

    urlpatters = [
        path(
            "django-e2ee-framework",
            include("django_e2ee.urls"),
        ),
    ]
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

from django.urls import include, path
from rest_framework import routers

from django_e2ee import views  # noqa: F401

#: App name for the django-e2ee-framework to be used in calls to
#: :func:`django.urls.reverse`
app_name = "e2ee"

router = routers.DefaultRouter()

router.register("master_keys", views.MasterKeyViewSet)
router.register("master_keysecrets", views.MasterKeySecretViewSet)
router.register("sessionkeys", views.SessionKeyViewSet)
router.register("encryptionkeys", views.EncryptionKeyViewSet)

urlpatterns = [
    path("", views.dummy_view, name="home"),
    path(
        "master_key/",
        views.MasterKeyRetrieveView.as_view(),
        name="master_key",
    ),
    path(
        "session_key/",
        views.SessionKeyUpdateView.as_view(),
        name="session_key",
    ),
    path(
        "encryptionkeys/<pk>/secrets/",
        views.EncryptionKeySecretView.as_view(),
        name="encryptionkeysecret",
    ),
    path("encrypt/", views.dummy_view, name="encrypt"),
    path("decrypt/", views.dummy_view, name="decrypt"),
    path("", include(router.urls)),
]
