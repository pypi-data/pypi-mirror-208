"""Context processors
------------------

Context processors for the django_e2ee app.
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

from typing import TYPE_CHECKING, Any, Dict

from django.urls import reverse

from django_e2ee import forms

if TYPE_CHECKING:
    from django_e2ee import models


def get_e2ee_login_context_data(request) -> Dict:
    context: Dict[str, Any] = {}
    if not hasattr(request.user, "master_key"):
        context["e2ee_login_url"] = reverse("e2ee:masterkey-list")
        context["e2ee_login_form"] = forms.PasswordCreateForm()
    else:
        context["e2ee_login_url"] = reverse("e2ee:sessionkey-list")
        master_key: models.MasterKey = request.user.master_key
        context["e2ee_login_form"] = form = forms.PasswordInputForm(
            initial={"uuid": master_key.masterkeysecret_set.first()}
        )
        form.fields["uuid"].queryset = master_key.masterkeysecret_set.all()  # type: ignore
    return context
