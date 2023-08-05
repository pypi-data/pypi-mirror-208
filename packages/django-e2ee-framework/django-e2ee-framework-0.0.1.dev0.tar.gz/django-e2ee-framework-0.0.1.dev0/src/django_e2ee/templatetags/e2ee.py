"""E2EE template tags
------------------

Template tags for the django-e2ee-framework.
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

from typing import TYPE_CHECKING, Optional, Union

from django import template

from django_e2ee import forms, models

if TYPE_CHECKING:
    from django.contrib.auth.models import User
    from django.contrib.sessions.backends.db import SessionStore
    from django.contrib.sessions.models import Session
    from django.db.models import QuerySet

register = template.Library()


@register.filter
def has_session_key(session: Union[str, SessionStore, Session]) -> bool:
    """Test if a session has e2e enabled."""
    if not isinstance(session, str):
        session_key = session.session_key
    else:
        session_key = session
    return (
        models.SessionKey.objects.filter(
            session__session_key=session_key
        ).first()
        is not None
    )


@register.filter
def e2ee_ignored(session: Union[str, SessionStore, Session]) -> bool:
    """Test if a session has e2e enabled."""
    if not isinstance(session, str):
        session_key = session.session_key
    else:
        session_key = session
    sessionkey = models.SessionKey.objects.filter(
        session__session_key=session_key
    ).first()
    return sessionkey is not None and sessionkey.ignore


@register.filter
def e2ee_enabled(session: Union[str, SessionStore, Session]) -> bool:
    """Test if a session has e2e enabled."""
    if not isinstance(session, str):
        session_key = session.session_key
    else:
        session_key = session
    return (
        models.SessionKey.objects.filter(
            session__session_key=session_key,
            secret__isnull=False,
        ).first()
        is not None
    )


@register.simple_tag
def get_session_key(
    session: Union[str, SessionStore, Session]
) -> Optional[models.SessionKey]:
    """Get the :model:`e2ee.SessionKey` for a session."""
    if not isinstance(session, str):
        session_key = session.session_key
    else:
        session_key = session
    return models.SessionKey.objects.filter(
        session__session_key=session_key
    ).first()


@register.simple_tag(takes_context=True)
def get_session_keys(context) -> QuerySet[models.SessionKey]:
    user: User = context["request"].user
    User_cls = user.__class__
    try:
        master_key: models.MasterKey = context["request"].user.master_key
    except (AttributeError, User_cls.master_key.RelatedObjectDoesNotExist):  # type: ignore
        return models.SessionKey.objects.none()
    else:
        return models.SessionKey.objects.filter(master_key=master_key)


@register.simple_tag
def get_password_create_form():
    return forms.PasswordCreateForm()


@register.simple_tag(takes_context=True)
def get_session_key_form(context, session_key) -> forms.E2EESessionForm:
    """Get a form to enable the session verification."""
    request = context["request"]
    session = request.session
    keep_uuid = True
    has_master_key = hasattr(request.user, "master_key")
    try:
        sessionkey = models.SessionKey.objects.get(
            session=session.session_key,
            secret__isnull=False,
        )
    except models.SessionKey.DoesNotExist:
        pass
    else:
        if sessionkey.secret:
            keep_uuid = False
    initial = {"session_secret": session_key.session_secret}

    # update the initial value for the masterkey secret
    if keep_uuid:
        if has_master_key:
            master_key: models.MasterKey = request.user.master_key
            initial["uuid"] = master_key.masterkeysecret_set.first()

    form = forms.E2EESessionForm(initial=initial)

    # update the queryset for the secrets
    if keep_uuid:
        field = form.fields["uuid"]
        if has_master_key:
            field.queryset = master_key.masterkeysecret_set.all()  # type: ignore
        else:
            field.queryset = models.MasterKeySecret.objects.none()  # type: ignore
    else:
        del form.fields["uuid"], form.fields["password"]
    return form
