"""Tests for the django-e2ee-framework views
-----------------------------------------
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Dict, Optional

from django.urls import reverse

from django_e2ee import models

if TYPE_CHECKING:
    from django.contrib.auth.models import User
    from selenium.webdriver import Remote


def test_master_key_creation(e2e_browser: Remote, test_user: User):
    """Test the creation of the master key."""
    assert hasattr(test_user, "master_key")

    sessionid = e2e_browser.get_cookie("sessionid")["value"]  # type: ignore

    session_key = models.SessionKey.objects.get(session=sessionid)
    assert session_key.secret


def test_session_authentication(
    e2e_browser: Remote,
    test_user: User,
    authenticated_browser_factory: Callable[[User], Remote],
    make_request: Callable[[Remote, str, str, Optional[Dict]], Dict],
    dummy_password: str,
):
    """Test authentication of a new session via password."""
    browser = authenticated_browser_factory(test_user)
    sessionid = browser.get_cookie("sessionid")["value"]  # type: ignore

    uuid = test_user.master_key.masterkeysecret_set.first().uuid  # type: ignore

    response, body = make_request(
        browser,
        reverse("e2ee:sessionkey-list"),
        "POST",
        {"password": dummy_password, "uuid": str(uuid)},
    )

    assert response
    assert response["status"] == 201

    assert "session" in body
    assert body["session"] == sessionid

    assert "secret" in body and body["secret"]
    assert "signing_secret" in body and body["signing_secret"]
    assert "iv" in body and body["iv"]

    session_key = models.SessionKey.objects.get(session=sessionid)
    assert session_key.secret


def test_remote_session_authentication(
    e2e_browser: Remote,
    test_user: User,
    authenticated_browser_factory: Callable[[User], Remote],
    make_request: Callable[[Remote, str, str, Optional[Dict]], Dict],
):
    """Test authentication of a new session via other session."""
    browser = authenticated_browser_factory(test_user)

    browser.refresh()

    # push the encrypted session key to the server
    response, body = make_request(
        browser, reverse("e2ee:sessionkey-list"), "POST", {}
    )

    # make sure the request was successful
    assert response
    assert response["status"] == 201

    assert "verificationNumber" in body

    sessionid = browser.get_cookie("sessionid")["value"]  # type: ignore

    session_key = models.SessionKey.objects.get(session=sessionid)
    assert not session_key.secret
    assert session_key.session_secret

    # enable the session from the other device
    response, body = make_request(
        e2e_browser,
        reverse("e2ee:sessionkey-detail", args=(sessionid,)),
        "PATCH",
        body,
    )

    assert response
    assert "session_secret" in body and not body["session_secret"]
    assert "secret" in body and body["secret"]
    assert "signing_secret" in body and body["signing_secret"]

    session_key = models.SessionKey.objects.get(session=sessionid)
    assert session_key.secret
    assert session_key.signing_secret
    assert not session_key.session_secret


def test_master_key_secret_creation(
    e2e_browser: Remote,
    make_request: Callable[[Remote, str, str, Optional[Dict]], Dict],
    authenticated_browser_factory: Callable[[User], Remote],
    test_user: User,
    dummy_password: str,
):
    """Test the creation of another masterkey secret."""

    # make sure everything worked as it should for the initial master key
    test_master_key_creation(e2e_browser, test_user)

    response, body = make_request(
        e2e_browser,
        reverse("e2ee:masterkeysecret-list"),
        "POST",
        {"password": dummy_password + "2", "identifier": "Another secret"},
    )

    assert response
    assert response["status"] == 201

    assert "uuid" in body
    assert models.MasterKeySecret.objects.filter(
        uuid=body["uuid"], master_key=test_user.master_key
    )

    # now try to login with this new secret
    browser = authenticated_browser_factory(test_user)
    sessionid = browser.get_cookie("sessionid")["value"]  # type: ignore

    response, body = make_request(
        browser,
        reverse("e2ee:sessionkey-list"),
        "POST",
        {"password": dummy_password + "2", "uuid": body["uuid"]},
    )

    assert response
    assert response["status"] == 201

    assert "session" in body
    assert body["session"] == sessionid

    assert "secret" in body and body["secret"]
    assert "signing_secret" in body and body["signing_secret"]
    assert "iv" in body and body["iv"]

    session_key = models.SessionKey.objects.get(session=sessionid)
    assert session_key.secret


def test_remote_password_authentication(
    e2e_browser: Remote,
    test_user: User,
    authenticated_browser_factory: Callable[[User], Remote],
    make_request: Callable[[Remote, str, str, Optional[Dict]], Dict],
    dummy_password: str,
):
    """Test authentication of a new session via other session and password."""
    browser = authenticated_browser_factory(test_user)
    browser2 = authenticated_browser_factory(test_user)

    browser.refresh()

    # push the encrypted session key to the server
    response, body = make_request(
        browser, reverse("e2ee:sessionkey-list"), "POST", {}
    )

    # make sure the request was successful
    assert response
    assert response["status"] == 201

    assert "verificationNumber" in body

    sessionid = browser.get_cookie("sessionid")["value"]  # type: ignore

    session_key = models.SessionKey.objects.get(session=sessionid)
    assert not session_key.secret
    assert session_key.session_secret

    body["password"] = dummy_password
    secret: models.MasterKeySecret
    secret = test_user.master_key.masterkeysecret_set.first()  # type: ignore
    body["uuid"] = str(secret.uuid)

    # enable the session from the other device
    response, body = make_request(
        browser2,
        reverse("e2ee:sessionkey-detail", args=(sessionid,)),
        "PATCH",
        body,
    )

    assert response
    assert "session_secret" in body and not body["session_secret"]
    assert "secret" in body and body["secret"]
    assert "signing_secret" in body and body["signing_secret"]

    session_key = models.SessionKey.objects.get(session=sessionid)
    assert session_key.secret
    assert session_key.signing_secret
    assert not session_key.session_secret


def test_encryption_decryption_post(
    e2e_browser: Remote,
    test_user: User,
    make_request: Callable[[Remote, str, str, Optional[Dict]], Dict],
):
    """Test encrypting a message through the service worker."""
    response, body = make_request(
        e2e_browser,
        reverse("e2ee:encrypt"),
        "POST",
        {"message": "this-is a test!"},
    )

    assert response
    assert response["status"] == 200
    assert "message" in body
    assert "signature" in body
    assert "encryption_key" in body

    # test decryption without signaute check
    response, new_body = make_request(
        e2e_browser, reverse("e2ee:decrypt"), "POST", body
    )

    assert response
    assert response["status"] == 200
    assert "message" in new_body
    assert new_body["message"] == "this-is a test!"

    # test decryption with signature check
    body["signed_by"] = test_user.pk
    response, new_body = make_request(
        e2e_browser, reverse("e2ee:decrypt"), "POST", body
    )

    assert response
    assert response["status"] == 200
    assert "message" in new_body
    assert new_body["message"] == "this-is a test!"


class TestEncryptionKey:
    """Unit tests for the EncryptionKey class in JavaScript."""

    def get_encryption_key_js(self, driver: Remote):
        token = driver.get_cookie("csrftoken")["value"]  # type: ignore
        return f"""new EncryptionKey(
                {{
                'X-CSRFTOKEN': '{token}',
                'Content-Type': 'application/json'
                }},
                "{reverse("e2ee:home")}"
            )
        """

    def get_existing_encryption_key_js(self, driver: Remote, uuid):
        token = driver.get_cookie("csrftoken")["value"]  # type: ignore
        return f"""new ExistingEncryptionKey(
                {{
                'X-CSRFTOKEN': '{token}',
                'Content-Type': 'application/json'
                }},
                "{reverse("e2ee:home")}",
                "{uuid}"
            )
        """

    def test_key_generation(self, e2e_browser: Remote):
        """Test generating an encryption key."""
        encryption_key_code = self.get_encryption_key_js(e2e_browser)
        js = f"""
            var encryptionKey = {encryption_key_code}
            return encryptionKey.key.then(
                async (key) => await crypto.subtle.exportKey("jwk", key)
            )
        """
        key_data = e2e_browser.execute_script(js)

        assert key_data and "alg" in key_data

    def test_key_upload(self, e2e_browser: Remote):
        encryption_key_code = self.get_encryption_key_js(e2e_browser)
        js = f"""
            var encryptionKey = {encryption_key_code}
            return encryptionKey.createKey().then(
                async (d) => encryptionKey.uuid
            )
        """
        uuid = e2e_browser.execute_script(js)
        key = models.EncryptionKey.objects.filter(uuid=uuid).first()
        assert key
        assert len(key.encryptionkeysecret_set.all()) == 1

    def test_key_upload_for_other_user(
        self,
        test_user_factory: Callable[[], User],
        e2e_browser_factory: Callable[[User], Remote],
    ):
        user1 = test_user_factory()
        browser1 = e2e_browser_factory(user1)
        user2 = test_user_factory()
        browser2 = e2e_browser_factory(user2)

        # test the upload
        encryption_key_code = self.get_encryption_key_js(browser1)
        js = f"""
            var encryptionKey = {encryption_key_code}
            return encryptionKey.createKey().then(
                async (response) => await encryptionKey.uploadKeyForUser(
                    {user2.pk}
                ).then(response => encryptionKey.uuid)
            )
        """
        uuid = browser1.execute_script(js)
        key = models.EncryptionKey.objects.filter(uuid=uuid).first()
        assert key
        assert len(key.encryptionkeysecret_set.all()) == 2

        # now test the download
        encryption_key_code = self.get_existing_encryption_key_js(
            browser2, uuid
        )
        js = f"""
            var encryptionKey = {encryption_key_code}
            return encryptionKey.key.then(key => encryptionKey.uuid)
        """

        new_uuid = browser2.execute_script(js)
        assert uuid == new_uuid

    def test_key_upload_for_multiple_users(
        self,
        test_user_factory: Callable[[], User],
        e2e_browser_factory: Callable[[User], Remote],
    ):
        """Test the encryption key upload for multiple users."""
        user1 = test_user_factory()
        browser1 = e2e_browser_factory(user1)
        user2 = test_user_factory()
        browser2 = e2e_browser_factory(user2)
        user3 = test_user_factory()
        browser3 = e2e_browser_factory(user3)

        # test the upload
        encryption_key_code = self.get_encryption_key_js(browser1)
        js = f"""
            var encryptionKey = {encryption_key_code}
            return encryptionKey.createKey().then(
                async (response) => await encryptionKey.uploadKeyManyForUser(
                    [{user2.pk}, {user3.pk}]
                ).then(response => encryptionKey.uuid)
            )
        """
        uuid = browser1.execute_script(js)
        key = models.EncryptionKey.objects.filter(uuid=uuid).first()
        assert key
        assert len(key.encryptionkeysecret_set.all()) == 3

        # now test the download
        encryption_key_code = self.get_existing_encryption_key_js(
            browser2, uuid
        )
        js = f"""
            var encryptionKey = {encryption_key_code}
            return encryptionKey.key.then(key => encryptionKey.uuid)
        """

        new_uuid = browser3.execute_script(js)
        assert uuid == new_uuid

        encryption_key_code = self.get_existing_encryption_key_js(
            browser3, uuid
        )
        js = f"""
            var encryptionKey = {encryption_key_code}
            return encryptionKey.key.then(key => encryptionKey.uuid)
        """

        new_uuid = browser3.execute_script(js)
        assert uuid == new_uuid

    def test_encrypt_decrypt(
        self,
        e2e_browser: Remote,
    ):
        """Test encryption and decryption of a message."""
        encryption_key_code = self.get_encryption_key_js(e2e_browser)
        js = f"""
            var encryptionKey = {encryption_key_code}
            return encryptionKey.encrypt(
                base64ToArrayBuffer(btoa("this-is a test!"))
            ).then(
                async (cipherText) => encryptionKey.decrypt(
                    cipherText
                ).then(arrayBufferToBase64).then(atob)
            )
        """
        message = e2e_browser.execute_script(js)
        assert message == "this-is a test!"


class TestEncryptionKeyStore:
    """Unit tests for the EncryptionKey class in JavaScript."""

    def get_encryption_key_store_js(self, driver: Remote):
        token = driver.get_cookie("csrftoken")["value"]  # type: ignore
        return f"""new EncryptionKeyStore(
                {{
                'X-CSRFTOKEN': '{token}',
                'Content-Type': 'application/json'
                }},
                "{reverse("e2ee:home")}"
            )
        """

    def test_key_creation(self, e2e_browser: Remote):
        """Test the createKey method of an EncryptionKeyStore"""
        store_code = self.get_encryption_key_store_js(e2e_browser)
        js = f"""
            var encryptionKeyStore = {store_code}
            return encryptionKeyStore.createKey().then(key => key.uuid)
        """
        uuid = e2e_browser.execute_script(js)

        key = models.EncryptionKey.objects.filter(uuid=uuid).first()
        assert key
        assert len(key.encryptionkeysecret_set.all()) == 1

    def test_key_retrieval(self, e2e_browser: Remote):
        """Test the getKey method of an EncryptionKeyStore"""
        store_code = self.get_encryption_key_store_js(e2e_browser)
        js = f"""
            var encryptionKeyStore = {store_code}
            return encryptionKeyStore.createKey().then(key => key.uuid)
        """
        uuid = e2e_browser.execute_script(js)

        key = models.EncryptionKey.objects.filter(uuid=uuid).first()
        assert key
        assert len(key.encryptionkeysecret_set.all()) == 1

        js = f"""
            var encryptionKeyStore = {store_code}
            return encryptionKeyStore.getKey("{uuid}").then(key => key.uuid)
        """
        new_uuid = e2e_browser.execute_script(js)

        assert uuid == new_uuid

    def test_decryption(self, e2e_browser: Remote, test_user: User):
        """Test decrypting messages"""
        encryption_key_code1 = self.get_encryption_key_store_js(e2e_browser)
        encryption_key_code2 = self.get_encryption_key_store_js(e2e_browser)
        js = f"""
            var encryptionKeyStore1 = {encryption_key_code1}
            var encryptionKeyStore2 = {encryption_key_code2}
            return encryptionKeyStore1.createKey().then(
                encryptionKey => encryptionKey.encryptAndSignString(
                    "this-is a test!"
                ).then(
                    data => {{
                        data.encryption_key = encryptionKey.uuid;
                        data.signed_by = {test_user.pk};
                        return encryptionKeyStore2.decryptMessages(
                            [data, data]
                        )
                    }}
                )
            )
        """
        messages = e2e_browser.execute_script(js)
        assert len(messages) == 2
        assert messages == ["this-is a test!", "this-is a test!"]
