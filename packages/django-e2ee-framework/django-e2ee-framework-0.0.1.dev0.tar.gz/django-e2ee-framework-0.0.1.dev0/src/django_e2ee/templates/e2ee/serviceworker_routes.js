{% load static %}

importScripts('{% static "js/e2ee/utils.js" %}');
importScripts('https://cdn.jsdelivr.net/npm/idb-keyval@6/dist/umd.js');


async function handleMasterKeyPost({ url, request, event, params }) {

  let body = await request.json();

  let salt = crypto.getRandomValues(new Uint8Array(16))

  return generateKeyFromPassword(body.password, salt).then(
    async (wrappingKey) => {
      let masterKey = new MasterKey(
        request.headers,
        "{% url 'e2ee:home' %}"
      )
      return masterKey.uploadPublicKeys().then(
        async (response) => {
          if (response.status == 201) {
            return masterKey.uploadPrivateKeys(
              "{% url 'e2ee:masterkeysecret-list' %}",
              wrappingKey,
              "POST",
              {
                salt: arrayBufferToBase64(salt),
                identifier: body.identifier
              }
            )
          } else {
            return response;
          }
        }
      ).then(
        async (response) => {
          if (response.status == 201) {
            let sessionKey = await generateAESKey(["wrapKey", "unwrapKey"]);

            return idbKeyval.set("sessionKey", sessionKey).then(
              async () => masterKey.uploadPrivateKeys(
                '{% url "e2ee:sessionkey-list" %}',
                sessionKey,
                "POST"
              )
            )
          } else {
            return response
          }
        }
      )
    }
  )

}


async function handleMasterKeySecretPost({ url, request, event, params }) {

  let body = await request.json();

  let salt = crypto.getRandomValues(new Uint8Array(16))

  return generateKeyFromPassword(body.password, salt).then(
    async (wrappingKey) => {
      let masterKey = new MasterKeyFromSession(
        request.headers,
        "{% url 'e2ee:home' %}"
      );
      return masterKey.uploadPrivateKeys(
        "{% url 'e2ee:masterkeysecret-list' %}",
        wrappingKey,
        "POST",
        {
          salt: arrayBufferToBase64(salt),
          identifier: body.identifier
        }
      )
    }
  )
}


async function handleSessionKeyPost({ url, request, event, params }) {

  var masterKey;

  // get the public key and encrypt the sessionKey
  let body = await request.json();
  let sessionKey = await generateAESKey(["wrapKey", "unwrapKey"]);

  if (body.ignore) {
    return fetch(
      url, {
        method: "POST",
        headers: request.headers,
        body: JSON.stringify({ignore: true})
      }
    )
  }

  return idbKeyval.set("sessionKey", sessionKey).then(
    async function () {
      if (body.password) {
        masterKey = new MasterKeyFromPassword(
          request.headers,
          "{% url 'e2ee:home' %}",
          body.password,
          body.uuid
        )

        return masterKey.uploadPrivateKeys(
          url, sessionKey, "POST"
        )
      } else {
        // publish encrypted session secret to the server
        masterKey = new MasterKeyFromSession(
          request.headers,
          "{% url 'e2ee:home' %}"
        );
        return masterKey.wrapAESKey(sessionKey).then(
          async (sessionSecret) => {

            return fetch(
              url,
              {
                method: 'POST',
                headers: request.headers,
                body: JSON.stringify({
                  session_secret: arrayBufferToBase64(sessionSecret)
                })
              }
            ).then(async function (response) {
              let randomNumber = twoRandomDigits();
              return fetch("{% static 'js/e2ee/passwords.json' %}").then(
                async passwords => new Response(
                  JSON.stringify({
                    verificationNumber: await getVerificationNumber(
                      randomNumber, passwords[randomNumber], sessionSecret
                    ),
                    session_secret: arrayBufferToBase64(sessionSecret)
                  }),
                  {
                    headers: response.headers,
                    status: response.status,
                    statusText: response.statusText
                  }

                )
              )
            })
          }
        )
      }
    }
  )
}

async function handleForeignSessionKeyPatch({ url, request, event, params }) {

  let body = await request.json();

  // first validate the verificationNumber and then create the secret

  return fetch("{% static 'js/e2ee/passwords.json' %}").then(
    async function (passwords) {

      let requestValid = await verifyRequest(
        body.verificationNumber, passwords, base64ToArrayBuffer(body.session_secret)
      )
      if (!requestValid) {
        return new Response(
          '{"error": "Invalid verification number"}',
          {statusCode: 400, statusText: "Bad Request"}
        )
      }

      var masterKey;

      if (body.password) {
        masterKey = new MasterKeyFromPassword(
          request.headers,
          "{% url 'e2ee:home' %}",
          body.password,
          body.uuid
        );
      } else {
        masterKey = new MasterKeyFromSession(
          request.headers,
          "{% url 'e2ee:home' %}"
        );
      }

      return masterKey.unwrapSessionKey(
        body.session_secret
      ).then(
        async (sessionKey) => {
          return masterKey.uploadPrivateKeys(
            url, sessionKey, "PATCH", { session_secret: null }
          )
        }
      )
    }
  )
}

async function handleEncryptionPost({ url, request, event, params }) {
  let body = await request.json();

  if (typeof (body.message) === "undefined") {
    return new Response(
      '{"error": "No message to encrypt."}',
      {statusCode: 400, statusText: "Bad Request"}
    )
  }

  let encryptionKey;
  if (body.encryption_key) {
    encryptionKey = new ExistingEncryptionKey(
      request.headers, "{% url 'e2ee:home' %}", body.encryption_key
    );

  } else {
    encryptionKey = new EncryptionKey(
      request.headers, "{% url 'e2ee:home' %}"
    );
    await encryptionKey.createKey();
  }

  body = await encryptionKey.encryptAndSignString(
    body.message
  );
  body.encryption_key = encryptionKey.uuid;

  return new Response(
    JSON.stringify(body),
    {statusCode: 200, statusText: "OK"}
  )
}

async function handleDecryptionPost({ url, request, event, params }) {
  let body = await request.json();

  if (typeof (body.message) === "undefined") {
    return new Response(
      '{"error": "No message to decrypt."}',
      { statusCode: 400, statusText: "Bad Request" }
    )
  } else if (typeof (body.encryption_key) === "undefined") {
    return new Response(
      '{"error": "No encryption key specified."}',
      { statusCode: 400, statusText: "Bad Request" }
    )
  }

  let encryptionKey = new ExistingEncryptionKey(
    request.headers, "{% url 'e2ee:home' %}", body.encryption_key
  );

  return encryptionKey.decryptAndVerfiyString(
    body.message, body.signature, body.signed_by
  ).then(
    message => new Response(
      JSON.stringify({ message: message }),
      {statusCode: 200, statusText: "OK"}
    )
  ).catch((err) => new Response(
    JSON.stringify(err),
    {statusCode: 400, statusText: "Bad Request"}
  ))
}


workbox.routing.registerRoute(
  ({ url, request, event }) => {
    return url.pathname == "{% url 'e2ee:masterkey-list' %}";
  },
  handleMasterKeyPost,
  "POST"
);


workbox.routing.registerRoute(
  ({ url, request, event }) => {
    return url.pathname == "{% url 'e2ee:masterkeysecret-list' %}";
  },
  handleMasterKeySecretPost,
  "POST"
);


workbox.routing.registerRoute(
  ({ url, request, event }) => {
    return url.pathname == "{% url 'e2ee:sessionkey-list' %}";
  },
  handleSessionKeyPost,
  "POST"
);

workbox.routing.registerRoute(
  new RegExp('{% url "e2ee:sessionkey-list" %}.+/$'),
  handleForeignSessionKeyPatch,
  "PATCH"
);

workbox.routing.registerRoute(
  new RegExp('{% url "e2ee:encrypt" %}'),
  handleEncryptionPost,
  "POST"
);

workbox.routing.registerRoute(
  new RegExp('{% url "e2ee:decrypt" %}'),
  handleDecryptionPost,
  "POST"
);
