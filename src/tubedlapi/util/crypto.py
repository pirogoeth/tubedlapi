# -*- coding: utf-8 -*-

import base64
import os

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
from cryptography.hazmat.primitives.constant_time import bytes_eq
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend


class CryptProvider(object):
    ''' CryptProvider provides an encryption layer for data blobs.
        Given a secret, uses PBKDF2HMAC to stretch the key into
        a value suitable for encryption.

        CryptProvide will provide a simple encryption/decryption
        interface for performing crypto operations on blobs of data.
    '''

    key: bytes = None
    salt: bytes = None

    @classmethod
    def extract_salt_from_message(cls, message: bytes) -> bytes:
        ''' Extracts the salt used for the key which is used to
            encrypt a message blob.
        '''

        _, salt, _ = message.split(b'$')
        return salt

    def __init__(self, secret: bytes, iterations: int=10000, salt: bytes=None):
        ''' Creates a CryptProvider.

            Initializes the key which will be utilized in all
            encryption operations.

            Derived key length is not configurable as ChaCha20Poly1305
            expects a key with a length of 32 bytes.

            Key salt is stored on the class and written into the blob.
        '''

        self.salt = salt or os.urandom(16)
        if len(self.salt) != 16:
            raise ValueError('Salt must be 16 bytes in length')

        kdf = self._make_kdf(iterations=iterations)
        self.key = kdf.derive(secret)

    def _make_kdf(self, iterations: int=10000):
        ''' Creates a KDF that can be used for derivation or
            verification.

            Uses `self.salt` as the KDF salt.
            Raises `ValueError` if salt is not set.
            Raises `ValueError` if salt is not 16 bytes in length.
        '''

        if not self.salt:
            raise ValueError('Salt must be set')

        if len(self.salt) != 16:
            raise ValueError('Salt must be 16 bytes in length')

        return PBKDF2HMAC(
            algorithm=hashes.SHA512(),
            length=32,
            salt=self.salt,
            iterations=iterations,
            backend=default_backend(),
        )

    def encrypt_blob(self, blob: bytes) -> bytes:
        ''' Encrypts `blob` with ChaCha20Poly1305.

            Returns a bytes value (the "message") in the following form:

                {base64'd nonce}${base64'd salt}${base64'd blob}

            Expects `self.key` to be a 32-byte value.
        '''

        if not self.key:
            raise ValueError('Key must be set')

        if len(self.key) != 32:
            raise ValueError('Key must be 32 bytes in length')

        nonce = os.urandom(12)
        algo = ChaCha20Poly1305(self.key)

        enc_blob = algo.encrypt(nonce, blob, None)

        return '{nonce}${salt}${blob}'.format(
            nonce=base64.b64encode(nonce),
            salt=base64.b64encode(self.salt),
            blob=base64.b64encode(enc_blob),
        ).encode()

    def decrypt_message(self, message: bytes) -> bytes:
        ''' Disassembles and decrypts a message with the following form

                {base64'd nonce}${base64'd salt}${base64'd blob}

            Expects `self.key` to be a 32-byte value.
            Expects the message-encoded `salt` to equal `self.salt`.

            Returns the decrypted blob.
        '''

        if not self.key:
            raise ValueError('Key must be set')

        if len(self.key) != 32:
            raise ValueError('Key must be 32 bytes in length')

        nonce, salt, enc_blob = message.split(b'$')
        nonce = base64.b64decode(nonce)
        salt = base64.b64decode(salt)
        blob = base64.b64decode(enc_blob)

        return self.decrypt_blob(nonce, salt, blob)

    def decrypt_blob(self, nonce: bytes, salt: bytes, enc_blob: bytes) -> bytes:
        ''' Decrypts `enc_blob` using nonce and the initialized key.

            Expects `self.key` to be a 32-byte value.
            Expects the message-encoded `salt` to equal `self.salt`.

            Returns the decrypted blob.
        '''

        if not self.salt:
            raise ValueError('Salt must be set')

        if not bytes_eq(salt, self.salt):
            raise ValueError('Salts do not match.')

        algo = ChaCha20Poly1305(self.key)
        return algo.decrypt(nonce, enc_blob, None)
