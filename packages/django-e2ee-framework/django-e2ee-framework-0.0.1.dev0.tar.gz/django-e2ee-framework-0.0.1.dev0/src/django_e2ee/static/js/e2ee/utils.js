async function generateRSAKey(keyUsage=["wrapKey", "unwrapKey"]) {
  return crypto.subtle.generateKey(
    {
      name: "RSA-OAEP",
      modulusLength: 4096,
      publicExponent: new Uint8Array([1, 0, 1]),
      hash: "SHA-256"
    },
    true,
    keyUsage
  )
}

async function generateSigningKey(keyUsage = ["sign", "verify"]) {
  return crypto.subtle.generateKey(
    {
      name: "RSA-PSS",
      modulusLength: 4096,
      publicExponent: new Uint8Array([1, 0, 1]),
      hash: "SHA-256"
    },
    true,
    keyUsage
  )
}

async function generateAESKey(keyUsage = ["encrypt", "decrypt"]) {
  return crypto.subtle.generateKey(
    {
      name: "AES-GCM",
      length: 256
    },
    true,
    keyUsage
  );
}

function arrayBufferToBase64( buffer ) {
  var binary = '';
  var bytes = new Uint8Array( buffer );
  var len = bytes.byteLength;
  for (var i = 0; i < len; i++) {
  	binary += String.fromCharCode( bytes[ i ] );
  }
  return btoa( binary );
}

function base64ToArrayBuffer(base64) {
  var binary_string =  atob(base64);
  var len = binary_string.length;
  var bytes = new Uint8Array( len );
  for (var i = 0; i < len; i++)        {
      bytes[i] = binary_string.charCodeAt(i);
  }
  return bytes.buffer;
}

function toBinary(string) {
  // // taken from https://developer.mozilla.org/en-US/docs/Web/API/btoa
  const codeUnits = Uint16Array.from(
    { length: string.length },
    (element, index) => string.charCodeAt(index)
  );
  const charCodes = new Uint8Array(codeUnits.buffer);

  let result = "";
  charCodes.forEach((char) => {
    result += String.fromCharCode(char);
  });
  return result;
}

function fromBinary(binary) {
  // taken from https://developer.mozilla.org/en-US/docs/Web/API/btoa
  const bytes = Uint8Array.from({ length: binary.length }, (element, index) =>
    binary.charCodeAt(index)
  );
  const charCodes = new Uint16Array(bytes.buffer);

  let result = "";
  charCodes.forEach((char) => {
    result += String.fromCharCode(char);
  });
  return result;
}

function generatePem(pubKey) {
  return `-----BEGIN PUBLIC KEY-----\n${arrayBufferToBase64(pubKey)}\n-----END PUBLIC KEY-----`;
}

async function exportPublicKey(pubKey) {
  return crypto.subtle.exportKey(
    "spki", pubKey
  ).then(generatePem)
}

async function getMasterKeyMaterial(password) {
  const enc = new TextEncoder();
  return crypto.subtle.importKey(
    "raw",
    enc.encode(password),
    {name: "PBKDF2"},
    false,
    ["deriveBits", "deriveKey"]
  );
}

function importPEM(pem, keyUsages = ["wrapKey"]) {
  const pemHeader = "-----BEGIN PUBLIC KEY-----";
  const pemFooter = "-----END PUBLIC KEY-----";
  const pemContents = pem.substring(pemHeader.length, pem.length - pemFooter.length);
  return crypto.subtle.importKey(
    "spki",
    base64ToArrayBuffer(pemContents),
    {
      name: "RSA-OAEP",
      modulusLength: 4096,
      publicExponent: new Uint8Array([1, 0, 1]),
      hash: "SHA-256"
    },
    true,
    keyUsages
  )
}

function importSigningKey(pem, keyUsages = ["verify"]) {
  const pemHeader = "-----BEGIN PUBLIC KEY-----";
  const pemFooter = "-----END PUBLIC KEY-----";
  const pemContents = pem.substring(pemHeader.length, pem.length - pemFooter.length);
  return crypto.subtle.importKey(
    "spki",
    base64ToArrayBuffer(pemContents),
    {
      name: "RSA-PSS",
      modulusLength: 4096,
      publicExponent: new Uint8Array([1, 0, 1]),
      hash: "SHA-256"
    },
    true,
    keyUsages
  )
}


async function getMasterKey(
  keyMaterial, salt, keyUsage = ["wrapKey", "unwrapKey"]
) {
  return crypto.subtle.deriveKey(
    {
      "name": "PBKDF2",
      salt: salt,
      "iterations": 100000,
      "hash": "SHA-256"
    },
    keyMaterial,
    { "name": "AES-GCM", "length": 256},
    true,
    keyUsage
  );
}

async function generateKeyFromPassword(
  password, salt, keyUsage=["wrapKey", "unwrapKey"]
) {
  return getMasterKeyMaterial(password).then(
    keyMaterial => getMasterKey(keyMaterial, salt, keyUsage)
  )
}

async function wrapRSAKey(wrappingKey, keyToWrap, iv) {
  return crypto.subtle.wrapKey(
    "jwk",
    keyToWrap,
    wrappingKey,
    {
      name: "AES-GCM",
      iv: iv
    }
  );
}

async function wrapAESKey(wrappingKey, keyToWrap, iv) {
  return crypto.subtle.wrapKey(
    "jwk",
    keyToWrap,
    wrappingKey,
    {
      name: "RSA-OAEP"
    }
  );
}


async function unwrapRSAKey(unWrappingKey, wrappedKey, iv) {
  // 1. get the unwrapping key
  // 3. unwrap the key
  return crypto.subtle.unwrapKey(
    "jwk",                 // import format
    wrappedKey,      // ArrayBuffer representing key to unwrap
    unWrappingKey,         // CryptoKey representing key encryption key
    {                  // algorithm identifier for key encryption key
      name: "AES-GCM",
      iv: iv
    },
    {
      name: "RSA-OAEP",
      modulusLength: 4096,
      publicExponent: new Uint8Array([1, 0, 1]),
      hash: "SHA-256"
    },
    true,                  // extractability of key to unwrap
    ["unwrapKey"] // key usages for key to unwrap
  );
}


async function unwrapSigningKey(unWrappingKey, wrappedKey, iv) {
  // 1. get the unwrapping key
  // 3. unwrap the key
  return crypto.subtle.unwrapKey(
    "jwk",                 // import format
    wrappedKey,      // ArrayBuffer representing key to unwrap
    unWrappingKey,         // CryptoKey representing key encryption key
    {                  // algorithm identifier for key encryption key
      name: "AES-GCM",
      iv: iv
    },
    {
      name: "RSA-PSS",
      modulusLength: 4096,
      publicExponent: new Uint8Array([1, 0, 1]),
      hash: "SHA-256"
    },
    true,                  // extractability of key to unwrap
    ["sign"] // key usages for key to unwrap
  );
}


async function unwrapAESKey(
  unWrappingKey, wrappedKey, keyUsage = ["encrypt", "decrypt"]
) {
  // 1. get the unwrapping key
  // 3. unwrap the key
  return crypto.subtle.unwrapKey(
    "jwk",                 // import format
    wrappedKey,      // ArrayBuffer representing key to unwrap
    unWrappingKey,         // CryptoKey representing key encryption key
    {                  // algorithm identifier for key encryption key
      name: "RSA-OAEP",
    },
    {
      name: "AES-GCM",
      length: 256
    },
    true,                  // extractability of key to unwrap
    keyUsage // key usages for key to unwrap
  );
}

async function digestMessage(msg) {
  return crypto.subtle.digest('SHA-256', msg).then(                                 // hash the message
    function (hashBuffer) {
      const hashArray = Array.from(new Uint8Array(hashBuffer));                     // convert buffer to byte array
      const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join(''); // convert bytes to hex string
      return hashHex;
    }
  )
}


function twoRandomDigits() {
  // generate a random number between 10 and 99
  return Math.floor(Math.random() * (99 - 10 + 1) + 10)
}


function str2num(text) {
  // convert a string to a number
  let allCharacters = "0123456789abcdefghijklmnopqrstuvwxyz";
  let allCharactersData = allCharacters.split("");
  let characters = text.split("");
  let numbers = characters.map(char => allCharactersData.indexOf(char));
  return numbers.reduce((a, b) => a + b);
}

async function getVerificationNumber(randomNumber, password, message) {
  let salt = base64ToArrayBuffer("somesaltforpassword")
  return getMasterKeyMaterial(password).then(
    keyMaterial => crypto.subtle.deriveKey(
      {
        "name": "PBKDF2",
        salt: salt,
        "iterations": 1000,
        "hash": "SHA-256"
      },
      keyMaterial,
      { "name": "HMAC", "hash": "SHA-256" },
      true,
      ["sign"]
    )
  ).then(
    cryptoKey => crypto.subtle.sign(
      "HMAC", cryptoKey, message
    ).then(digestMessage).then(str2num)
  ).then(
    verificationNumber => parseInt(
      randomNumber.toString()
      + verificationNumber.toString().slice(-1)
    )
  )
}

async function verifyRequest(verificationNumber, passwords, message) {
  let randomNumber = parseInt(verificationNumber.toString().slice(0, 2))
  return getVerificationNumber(
    randomNumber, passwords[randomNumber], message
  ).then(generatedNumber => (verificationNumber == generatedNumber))
}


class ResourceDownloader {
  #requestHeaders;
  #baseUri;

  constructor(requestHeaders, baseUri) {

    this.#requestHeaders = requestHeaders;
    this.#baseUri = baseUri;

  }

  async getStoredPublicKeys() {
    return idbKeyval.get("publicKeys").then(
      async (keys) => {
        if (keys) {
          return keys
        } else {
          keys = { "publicKeys": {}, "publicSigningKeys": {} }
          await idbKeyval.set("publicKeys", keys)
          return keys
        }
      }
      )
  }

  async getPublicKeyForUser(user) {
    return this.getStoredPublicKeys().then(
      async (keys) => {
        // always download the public key for now as we do not yet have an
        // idea how to handle key reset properly
        return this.downloadPublicKeys(user, keys).then(keys => keys[0]);
        // if (typeof (keys.publicKeys[user]) === "undefined") {
        //   return this.downloadPublicKeys(user, keys).then(keys => keys[0]);
        // } else {
        //   return keys.publicKeys[user]
        // }
      }
    )
  }

  async getPublicSigningKeyForUser(user) {
    return this.getStoredPublicKeys().then(
      async (keys) => {
        // always download the public key for now as we do not yet have an
        // idea how to handle key reset properly
        return this.downloadPublicKeys(user, keys).then(keys => keys[1]);
        // if (typeof (keys.publicKeys[user]) === "undefined") {
        //   return this.downloadPublicKeys(user, keys).then(keys => keys[1]);
        // } else {
        //   return keys.publicSigningKeys[user]
        // }
      }
    )
  }

  async downloadPublicKeys(user, keys) {
    return this.fetch(`master_keys/${user}/`).then(
      async (response) => {
        if (response.status == 200) {
          let body = await response.json();
          var returnValue = [
            await importPEM(body.pubkey),
            await importSigningKey(body.signing_pubkey)
          ];
          [keys.publicKeys[user], keys.publicSigningKeys[user]] = returnValue;
          await idbKeyval.set("publicKeys", keys);
          return returnValue;
        } else {
          return response
        }
      }
    )
  }

  async fetch(path, body, resolve=true) {
    if (typeof (body) === "undefined") {
      body = {};
    }
    body.headers = this.#requestHeaders;
    if (!body.method) {
      body.method = "GET";
    }
    return fetch(
      resolve ? this.#baseUri + path : path,
      body
    )
  }
}


class MasterKeyBase extends ResourceDownloader {

  #keys;

  constructor(requestHeaders, baseUri) {

    super(requestHeaders, baseUri)
    this.#keys = {};

  }

  // ----------------- private keys ---------------------------

  async retrievePrivateKeys() {
    // to be implemented by subclasses. This method should return a list with
    // two items. the first one is the private key for encryption, the second
    // one is the private key for signing
    throw "Method has not been implemented!";
  }

  get privateKey() {
    if (typeof (this.#keys.privateKey) === "undefined") {
      return this.getPrivateKeys().then((keys) => keys[0]);
    } else {
      return Promise.resolve(this.#keys.privateKey);
    }
  }

  set privateKey(key) {
    this.#keys.privateKey = key;
  }

  get privateSigningKey() {
    if (typeof (this.#keys.privateSigningKey) === "undefined") {
      return this.getPrivateKeys().then((keys) => keys[1]);
    } else {
      return Promise.resolve(this.#keys.privateSigningKey);
    }
  }

  set publicKey(key) {
    this.#keys.privateSigningKey = key;
  }

  async getPrivateKeys() {
    if (
      (typeof (this.#keys.privateKey) === "undefined")
      || (typeof (this.#keys.privateSigningKey) === "undefined")
    ) {
      let privateKey, privateSigningKey;
      [privateKey, privateSigningKey] = await this.retrievePrivateKeys();
      this.#keys.privateKey = privateKey;
      this.#keys.privateSigningKey = privateSigningKey;
    }
    return [
      this.#keys.privateKey,
      this.#keys.privateSigningKey
    ]
  }

  get privateKeys() {
    return this.getPrivateKeys();
  }

  // ----------------- public keys ---------------------------

  async retrievePublicKeys() {
    // to be implemented by subclasses. This method should return a list with
    // two items. the first one is the public key for encryption, the second
    // one is the public key for signing
    throw "Method has not been implemented!";
  }

  get publicKey() {
    if (typeof (this.#keys.publicKey) === "undefined") {
      return this.getPublicKeys().then((keys) => keys[0]);
    } else {
      return Promise.resolve(this.#keys.publicKey);
    }
  }

  set publicKey(key) {
    this.#keys.publicKey = key;
  }

  get publicSigningKey() {
    if (typeof (this.#keys.publicSigningKey) === "undefined") {
      return this.getPublicKeys().then((keys) => keys[1]);
    } else {
      return Promise.resolve(this.#keys.publicSigningKey);
    }
  }

  set publicSigningKey(key) {
    this.#keys.publicSigningKey = key;
  }

  async getPublicKeys() {
    if (
      (typeof (this.#keys.publicKey) === "undefined")
      || (typeof (this.#keys.publicSigningKey) === "undefined")
    ) {
      let publicKey, publicSigningKey;
      [publicKey, publicSigningKey] = await this.retrievePublicKeys();
      this.#keys.publicKey = publicKey;
      this.#keys.publicSigningKey = publicSigningKey;
    }
    return [
      this.#keys.publicKey,
      this.#keys.publicSigningKey
    ]
  }

  get publicKeys() {
    return this.getPublicKeys();
  }

  async unwrapSessionKey(sessionSecret) {
    return unwrapAESKey(
      await this.privateKey,
      base64ToArrayBuffer(sessionSecret),
      ["wrapKey", "unwrapKey"]
    )
  }

  async unwrapEncryptionKey(encryptionSecret) {
    return unwrapAESKey(
      await this.privateKey,
      base64ToArrayBuffer(encryptionSecret)
    )
  }

  async wrapAESKey(sessionKey) {
    // wrap a symmetric (e.g. AES) key
    return this.publicKey.then((key) => wrapAESKey(key, sessionKey));
  }

  async wrapPrivateKeys(sessionKey) {
    // wrap the private keys with a symmetric (e.g. AES) key
    let iv = crypto.getRandomValues(new Uint8Array(12));
    let wrappedKey = wrapRSAKey(
      sessionKey, await this.privateKey, iv
    ).then(arrayBufferToBase64);
    let wrappedSigningKey = wrapRSAKey(
      sessionKey, await this.privateSigningKey, iv
    ).then(arrayBufferToBase64);
    return {
      iv: iv,
      secret: await wrappedKey,
      signing_secret: await wrappedSigningKey
    }
  }

  async uploadPublicKeys(path="master_keys/", method = "POST", resolve=true) {
    return this.publicKeys.then(
      async ([pubKey, publicSigningKey]) => {
        let exportedPubKey = exportPublicKey(pubKey);
        let exportedPublicSigningKey = exportPublicKey(publicSigningKey);
        return this.fetch(
          path,
          {
            method: method,
            body: JSON.stringify(
              {
                pubkey: await exportedPubKey,
                signing_pubkey: await exportedPublicSigningKey
              }
            )
          },
          resolve
        )
      }
    )
  }

  async uploadPrivateKeys(path, sessionKey, method = "PATCH", data = {}) {
    return this.wrapPrivateKeys(sessionKey).then(
      async (exportedKeys) => {
        exportedKeys.iv = arrayBufferToBase64(exportedKeys.iv)
        return this.fetch(
          path,
          {
            method: method,
            body: JSON.stringify({ ...data, ...exportedKeys })
          },
          false
        )
      }
    )
  }

  async sign(message) {
    return crypto.subtle.sign(
      {
        name: "RSA-PSS",
        saltLength: 32,
      },
      await this.privateSigningKey,
      message
    )
  }

  async verify(signature, message) {
    return crypto.subtle.verify(
      {
        name: "RSA-PSS",
        saltLength: 32,
      },
      await this.publicSigningKey,
      signature,
      message
    )
  }
}


class MasterKey extends MasterKeyBase {

  #keyPair;
  #signingKeyPair;

  async #buildKeys() {
    [this.#keyPair, this.#signingKeyPair] = await Promise.all(
      [
        generateRSAKey(),
        generateSigningKey()
      ]
    )
  }

  async retrievePrivateKeys() {
    if (typeof (this.#keyPair) === "undefined") {
      await this.#buildKeys();
    }
    return [
      this.#keyPair.privateKey,
      this.#signingKeyPair.privateKey
    ]
  }

  async retrievePublicKeys() {
    if (typeof (this.#keyPair) === "undefined") {
      await this.#buildKeys();
    }
    return [
      this.#keyPair.publicKey,
      this.#signingKeyPair.publicKey
    ]
  }
}


const retrievePublicKeysMixin = (Base) => class extends Base {
  async retrievePublicKeys() {
    return this.fetch("master_key/").then(async (response) => {
      if (response.status == 200) {
        let body = await response.json();
        return [
          await importPEM(body.pubkey),
          await importSigningKey(body.signing_pubkey)
        ]
      } else {
        return response
      }
    })
  }
}


class MasterKeyFromPassword extends retrievePublicKeysMixin(MasterKeyBase) {

  #password;
  #uuid;
  constructor(requestHeaders, baseUri, password, uuid) {
    super(requestHeaders, baseUri)
    this.#password = password;
    this.#uuid = uuid;
  }

  async retrievePrivateKeys() {
    return this.fetch(
      "master_keysecrets/" + this.#uuid + "/"
    ).then(async (response) => {
      if (response.status == 200) {
        let privateKeyData = await response.json();
        return generateKeyFromPassword(
          this.#password, base64ToArrayBuffer(privateKeyData.salt)
        ).then(
          async unWrappingKey => {
            return [
              await unwrapRSAKey(
                unWrappingKey,
                base64ToArrayBuffer(privateKeyData.secret),
                base64ToArrayBuffer(privateKeyData.iv)
              ),
              await unwrapSigningKey(
                unWrappingKey,
                base64ToArrayBuffer(privateKeyData.signing_secret),
                base64ToArrayBuffer(privateKeyData.iv)
              ),
            ]
          })
      } else {
        throw `Invalid response with status ${response.status}: ${await response.json()}`;
      }
    })
  }
}


class MasterKeyFromSession extends retrievePublicKeysMixin(MasterKeyBase) {

  async retrievePrivateKeys() {
    return this.fetch(
      "session_key/"
    ).then(async (response) => {
      if (response.status == 200) {
        let privateKeyData = await response.json();
        return idbKeyval.get("sessionKey").then(
          async unWrappingKey => [
            await unwrapRSAKey(
              unWrappingKey,
              base64ToArrayBuffer(privateKeyData.secret),
              base64ToArrayBuffer(privateKeyData.iv)
            ),
            await unwrapSigningKey(
              unWrappingKey,
              base64ToArrayBuffer(privateKeyData.signing_secret),
              base64ToArrayBuffer(privateKeyData.iv)
            ),
          ]
        )
      } else {
        return response
      }
    })
  }

}


class EncryptionKey extends ResourceDownloader {

  #key;
  #uuid;

  constructor(requestHeaders, baseUri, uuid, masterKey) {

    super(requestHeaders, baseUri);

    if (typeof (masterKey) === "undefined") {
      this.masterKey = new MasterKeyFromSession(requestHeaders, baseUri)
    } else {
      this.masterKey = masterKey
    }
    this.#uuid = uuid
  }

  async retrieveKey() {
    return generateAESKey()
  }

  get key() {
    if (typeof (this.#key) === "undefined") {
      return this.retrieveKey().then(
        (key) => {
          this.#key = key;
          return key
        }
      );
    } else {
      return Promise.resolve(this.#key)
    }
  }

  set key(key) {
    this.#key = key;
  }

  async getKeySignature(publicKey) {
    if (typeof (publicKey) === "undefined") {
      return this.masterKey.publicKey.then(
        publicKey => this.key.then(
          key => this.masterKey.sign(this.prependIdentifer(publicKey, key))
        )
      )
    } else {
      return this.key.then(
        key => this.masterKey.sign(
          this.prependIdentifer(publicKey, key)
        )
      )
    }
  }

  async verifyKey() {
    return true
  }

  async wrapKey(publicKey) {
    if (typeof (publicKey) === "undefined") {
      publicKey = await this.masterKey.publicKey
    }
    return wrapAESKey(publicKey, await this.key)
  }

  prependIdentifer(identifier, message) {
    let encodedMessage = new Uint8Array(message);
    let encodedIdentifier = new Uint8Array(
      base64ToArrayBuffer(btoa(JSON.stringify(identifier)))
    );
    let combinedMessage = new Uint8Array(
      encodedIdentifier.length + encodedMessage.length
    );
    combinedMessage.set(encodedIdentifier, 0)
    combinedMessage.set(encodedMessage, encodedIdentifier.length)
    return combinedMessage
  }

  async createKey() {
    return this.fetch(
      "encryptionkeys/",
      {
        method: "POST",
        body: JSON.stringify({
          uuid: this.uuid
        })
      }
    ).then(response => response.status == 201 ? this.uploadKey() : response)
  }

  async uploadKeyManyForUser(users) {
    return Promise.all(
      users.map(user => this.getPublicKeyForUser(user))
    ).then(publicKeys => this.uploadKeyMany(publicKeys))
  }

  async uploadKeyMany(publicKeys) {
    // upload the key for multiple public keys
    return Promise.all(
      publicKeys.map(
        async (publicKey) => {
          return {
            secret: await this.wrapKey(publicKey).then(arrayBufferToBase64),
            signature: await this.getKeySignature(publicKey).then(arrayBufferToBase64),
            encrypted_with: await exportPublicKey(publicKey)
          }
        })
    ).then(
      body => this.fetch(
        `encryptionkeys/${this.uuid}/secrets/`,
        {
          method: "POST",
          body: JSON.stringify(body)
        }
      )
    )
  }

  async uploadKeyForUser(user) {
    return this.uploadKey(await this.getPublicKeyForUser(user))
  }

  async uploadKey(publicKey) {
    if (typeof (publicKey) === "undefined") {
      publicKey = await this.masterKey.publicKey
    }
    return this.fetch(
      `encryptionkeys/${this.uuid}/secrets/`,
      {
        method: "POST",
        body: JSON.stringify({
          secret: await this.wrapKey(publicKey).then(arrayBufferToBase64),
          signature: await this.getKeySignature(publicKey).then(arrayBufferToBase64),
          encrypted_with: await exportPublicKey(publicKey)
        })
      }
    )
  }

  get uuid() {
    if (typeof (this.#uuid) === "undefined") {
      this.#uuid = crypto.randomUUID();
    }
    return this.#uuid
  }

  set uuid(value) {
    this.#uuid = value;
  }

  async getMessageSignature(message, identifier) {
    if (identifier) {
      message = this.prependIdentifer(identifier, message)
    }
    return this.masterKey.sign(
      this.prependIdentifer(this.uuid, message)
    )
  }

  async verifyMessageSignatureForUser(signature, message, user, identifier) {
    return this.verifyMessageSignature(
      signature, message, await this.getPublicSigningKeyForUser(user), identifier
    )
  }

  async verifyMessageSignature(signature, message, publicSigningKey, identifier) {
    if (identifier) {
      message = this.prependIdentifer(identifier, message)
    }
    return crypto.subtle.verify(
      {
        name: "RSA-PSS",
        saltLength: 32
      },
      publicSigningKey,
      signature,
      this.prependIdentifer(this.uuid, message)
    )
  }

  async encryptAndSignString(message) {
    let buffer = base64ToArrayBuffer(btoa(toBinary(message)));
    let cipherText = await this.encrypt(buffer);
    let iv = cipherText.slice(0, 12);
    return {
      message: arrayBufferToBase64(cipherText),
      signature: await this.getMessageSignature(
        buffer, atob(arrayBufferToBase64(iv))
      ).then(arrayBufferToBase64)
    }
  }

  async decryptAndVerfiyString(encryptedMessage, signature, signed_by) {
    let cipherText = base64ToArrayBuffer(encryptedMessage);
    let message = await this.decrypt(cipherText);
    let iv = cipherText.slice(0, 12);
    if ((signature) && (signed_by)) {
      let valid = await this.verifyMessageSignatureForUser(
        base64ToArrayBuffer(signature),
        message,
        signed_by,
        atob(arrayBufferToBase64(iv))
      )
      if (!valid) {
        throw "Signature and message do not match!"
      }
    }
    return fromBinary(atob(arrayBufferToBase64(message)))
  }

  async encrypt(message) {
    let iv = crypto.getRandomValues(new Uint8Array(12));
    return this.key.then(
      key => crypto.subtle.encrypt(
        { name: "AES-GCM", iv },
        key,
        message
      )
    ).then(
      encryptedMessage => {
        let cipherText = new Uint8Array(encryptedMessage);
        let output = new Uint8Array(iv.length + cipherText.length);
        output.set(iv, 0);
        output.set(cipherText, iv.length);
        return output
      }
    )
  }

  async decrypt(cipherText) {
    return this.decryptMessage(
      cipherText.slice(0, 12), cipherText.slice(12)
    )
  }

  async decryptMessage(iv, message) {
    return this.key.then(
      key => crypto.subtle.decrypt(
        { name: "AES-GCM", iv: iv }, key, message
      )
    )
  }

}


class ExistingEncryptionKey extends EncryptionKey {

  async retrieveKey() {
    return this.fetch(
      `encryptionkeys/${this.uuid}/secrets/`,
    ).then(
      (response) => {
        if (response.status == 200) {
          return response.json().then(
            (body) => this.unwrapAndVerify(body))
        } else {
          console.error(response);
          throw "Could not retrieve encryption key!"
        }
      }
    )
  }

  async unwrapAndVerify(body) {
    return this.masterKey.unwrapEncryptionKey(
      body.secret
    ).then(
      async (key) => crypto.subtle.verify(
        {
          name: "RSA-PSS",
          saltLength: 32,
        },
        await this.getPublicSigningKeyForUser(body.signed_by),
        base64ToArrayBuffer(body.signature),
        this.prependIdentifer(await this.masterKey.publicKey, key)
      ).then(result => {
        if (result) {
          return key
        } else {
          throw "Signature of the encryption key does not match!"
        }
      })
    )
  }

}

class DownloadedEncryptionKey extends ExistingEncryptionKey {

  #keyData;

  constructor(requestHeaders, baseUri, keyData, masterKey) {
    super(requestHeaders, baseUri, keyData.encryption_key, masterKey);
    this.#keyData = keyData;
  }

  async retrieveKey() {
    return this.unwrapAndVerify(this.#keyData);
  }
}


class EncryptionKeyStore extends ResourceDownloader {

  #masterKey;
  #keyParams;
  #keys;

  constructor(requestHeaders, baseUri, masterKey) {

    super(requestHeaders, baseUri);

    if (typeof (masterKey) === "undefined") {
      this.#masterKey = new MasterKeyFromSession(requestHeaders, baseUri);
    } else {
      this.#masterKey = masterKey;
    }
    this.#keys = {};

    this.#keyParams = [
      requestHeaders,
      baseUri
    ];

  }

  #getKeyParams(uuid) {
    return this.#keyParams.concat([uuid, this.#masterKey])
  }

  async extractKeys(messages) {
    let existingKeys = Object.keys(this.#keys);
    let promises = [];
    messages.forEach(
      attrs => {
        let uuid = attrs.encryption_key;
        if (
          uuid
          && (!existingKeys.includes(uuid))
        ) {
          existingKeys.push(uuid);
          let key = new ExistingEncryptionKey(...this.#getKeyParams(uuid));
          promises.push(key.retrieveKey().then(() => key));
          this.#keys[uuid] = key;
        }
      }
    )
    return Promise.all(promises);
  }

  async createKey(uuid) {
    if (typeof (uuid) === "undefined") {
      uuid = crypto.randomUUID()
    }
    let key = new EncryptionKey(...this.#getKeyParams(uuid));
    return key.createKey().then(() => key);
  }

  async getKey(uuid) {
    if (typeof (uuid) === "undefined") {
      throw "Need uuid of the encryption key!"
    } else if (this.#keys[uuid]) {
      return Promise.resolve(this.#keys[uuid]);
    } else {
      let key = new ExistingEncryptionKey(...this.#getKeyParams(uuid));
      this.#keys[uuid] = key;
      return key.key.then(() => key)
    }
  }

  async decryptMessages(messages) {
    await this.extractKeys(messages);
    return Promise.all(
      messages.map(
        message => {
          if (message.encryption_key) {
            return this
              .getKey(message.encryption_key)
              .then(
                key => key.decryptAndVerfiyString(
                  message.message,
                  message.signature,
                  message.signed_by
                )
              )
          } else {
            return message.message;
          }
        }
      )
    )
  }

}
