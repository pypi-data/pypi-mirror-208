"""Reusable forms of the django-e2ee-framework."""

# Disclaimer
# ----------
#
# Copyright (C) 2022 Helmholtz-Zentrum Hereon
#
# This file is part of the project django-e2ee-framework
# and is released under the EUPL-1.2 license. See LICENSE in the root of the
# repository for full licensing details.
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

from django import forms

from django_e2ee import models


class PasswordCreateForm(forms.Form):
    """A form for creting the E2EE-password."""

    class Media:
        js = (
            "js/e2ee/submit_form_as_json.js",
            "js/e2ee/password_generator.js",
            "js/e2ee/fill_random_password.js",
        )

    identifier = forms.CharField(
        max_length=100,
        help_text="""
          Enter an identifier for your password. The identifier can be used to
          distinguish multiple E2EE passwords. You can have one for regular
          usage, and one for backup for instance.
        """,
        initial="Random passphrase",
    )

    password = forms.CharField(
        help_text=(
            "Enter a new password or passphrase to enable end-to-end "
            "encryption. Please choose a strong password and store it in a "
            "safe place. Server admins will not be able to recover end-to-end "
            "encrypted data if you loose your password."
        ),
        strip=False,
        widget=forms.PasswordInput(
            attrs={"autocomplete": "new-password", "autofocus": True}
        ),
    )

    show_password = forms.BooleanField(
        help_text="Toggle password visibility",
        initial=False,
        required=False,
        widget=forms.CheckboxInput(attrs={"data-password-visibility": True}),
    )


class PasswordInputForm(forms.Form):
    """A form for entering the E2EE-password."""

    class Media:
        js = ("js/e2ee/submit_form_as_json.js",)

    uuid = forms.ModelChoiceField(
        queryset=models.MasterKeySecret.objects.all(),
        help_text=(
            "The identifier that you specified when you created the password"
        ),
        label="Identifier",
    )

    password = forms.CharField(
        help_text="Enter your End-To-End-Encryption password or passphrase.",
        strip=False,
        widget=forms.PasswordInput(
            attrs={"autocomplete": "current-password", "autofocus": True}
        ),
    )


class E2EESessionForm(PasswordInputForm):
    """A form to setup E2EE for a session"""

    verification_number = forms.IntegerField(
        max_value=999,
        min_value=100,
        help_text=(
            "Enter the verification number that has been displayed on your "
            "other device."
        ),
    )

    session_secret = forms.CharField(widget=forms.HiddenInput)

    method = forms.CharField(initial="PATCH", widget=forms.HiddenInput)

    def add_prefix(self, field_name):
        if field_name == "verification_number":
            return "verificationNumber"
        return super().add_prefix(field_name)
