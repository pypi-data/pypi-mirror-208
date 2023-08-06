"""Cryptography module for FlashPass"""
import os
import typing as t

from cryptography.hazmat.primitives.ciphers import Cipher
from cryptography.hazmat.primitives.ciphers.algorithms import AES
from cryptography.hazmat.primitives.ciphers.modes import CBC
from cryptography.hazmat.primitives.hashes import SHA256, SHA512, Hash
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.padding import PKCS7

from flashpass.exceptions import (
    InvalidPasswordError,
    IVLengthError,
    IVMissingError,
    KeyLengthError,
    KeyMissingError,
    SaltLengthError,
    SaltMissingError,
)

ITERATIONS = 20560
KEY_LENGTH = 32
SALT_LENGTH = 16
IV_LENGTH = 16
HASH_LENGTH = 32


def gen_salt() -> bytes:
    """Generates cryptographically secure random bytes to be used as salt

    Returns:
        bytes: the generated salt
    """
    return os.urandom(SALT_LENGTH)


def gen_iv() -> bytes:
    """generates cryptographically secure random bytes to be used as iv

    Returns:
        bytes: the generated iv
    """
    return os.urandom(IV_LENGTH)


def gen_key(password: str, salt: bytes) -> bytes:
    """generates a hashed key.

    Params:
        password: the password to wrap
        salt: the salt to use for PBKDF2

    Returns:
        bytes: the hashed key
    """
    if len(salt) != SALT_LENGTH:
        raise SaltLengthError(salt, SALT_LENGTH)
    kdf = PBKDF2HMAC(
        algorithm=SHA512(), length=KEY_LENGTH, salt=salt, iterations=ITERATIONS
    )
    return kdf.derive(password.encode("utf-8"))


def hash_key(key: bytes) -> bytes:
    """hashes a key.

    Params:
        key: the key to hash

    Returns:
        bytes: the hashed key
    """
    digest = Hash(SHA256())
    digest.update(key)
    return digest.finalize()


class SaltedKey:
    """data class for a hashed key and its salt.

    WARNING: There is no guarantee that the salt attribute of SaltedKey
    objects were used to derive the key attribute.

    Params:
        password (optional): password to hash. If no password is provided,
            returns a blank key

    Properties:
        key: The hashed key
        salt: The hashed key's salt
    """

    def __init__(self, password: t.Optional[str] = None) -> None:
        self._salt: t.Optional[bytes] = None
        self._key: t.Optional[bytes] = None
        if password is not None:
            self._salt = gen_salt()
            self._key = gen_key(password, self.salt)

    @property
    def salt(self) -> bytes:
        """property for the salt's bytes.

        Returns:
            bytes: the salt portion of the SaltedKey

        Raises:
            SaltMissingError: if the key was not initialized
        """
        if self._salt is None:
            raise SaltMissingError()
        return self._salt

    @salt.setter
    def salt(self, salt: bytes) -> None:
        """setter for the salt property.

        Params:
            salt: the salt to set as this key's salt

        Raises:
            SaltLengthError: if the provided salt is not the correct length
        """
        if len(salt) != SALT_LENGTH:
            raise SaltLengthError(salt, SALT_LENGTH)
        self._salt = salt

    @property
    def key(self) -> bytes:
        """property for the key's bytes.

        Returns:
            bytes: the key portion of the SaltedKey

        Raises:
            KeyMissingError: if the key was not initialized
        """
        if self._key is None:
            raise KeyMissingError()
        return self._key

    @key.setter
    def key(self, key: bytes) -> None:
        """setter for the key property.

        Params:
            key: the key to set as this key's key

        Raises:
            KeyLengthError: if the provided key is not the correct length
        """
        if len(key) != KEY_LENGTH:
            raise KeyLengthError(key, KEY_LENGTH)
        self._key = key

    @classmethod
    def from_bytes(cls: t.Type["SaltedKey"], key: bytes, salt: bytes) -> "SaltedKey":
        """Creates a new SaltedKey using given parameters.

        Args:
            key (bytes): The key to use for the SaltedKey.
            salt (bytes): The salt to use for the SaltedKey.
        """
        salted_key = cls()
        salted_key.key = key
        salted_key.salt = salt
        return salted_key


class FpCipher:
    """cipher for encrypting and decrypting .fp files.

    Params:
        iv (optional): iv to use. If not provided, a random iv is generated

    Properties:
        iv: the cipher's iv
    """

    def __init__(
        self, iv: t.Optional[bytes] = None  # pylint: disable=invalid-name
    ) -> None:
        self._iv = iv if iv is not None else gen_iv()

    @property
    def iv(self) -> bytes:  # pylint: disable=invalid-name
        """property for the cipher's iv.

        Returns:
            bytes: the iv used for the cipher

        Raises:
            IVMissingError: if the Cipher was not initialized with an iv
        """
        if self._iv is None:
            raise IVMissingError()
        return self._iv

    @iv.setter
    def iv(self, iv: bytes) -> None:  # pylint: disable=invalid-name
        """setter for the iv property.

        Params:
            iv: the iv to set as this cipher's iv

        Raises:
            IVLengthError: if the provided iv is not the correct length
        """
        if len(iv) != IV_LENGTH:
            raise IVLengthError(iv, IV_LENGTH)
        self._iv = iv

    def encrypt_message(self, plaintext: bytes, salted_key: SaltedKey) -> bytes:
        """encrypt plaintext using a SaltedKey.

        Parameters:
            plaintext: the string to encrypt
            salted_key: the key to use for encryption

        Raises:
            CipherNotInitializedError: if the Cipher was not initialized with an iv
        """
        cipher = Cipher(AES(salted_key.key), CBC(self.iv))
        encryptor = cipher.encryptor()
        padder = PKCS7(KEY_LENGTH * 8).padder()
        padded_text = padder.update(plaintext) + padder.finalize()
        ciphertext: bytes = encryptor.update(padded_text) + encryptor.finalize()
        return ciphertext

    def decrypt_message(self, ciphertext: bytes, salted_key: SaltedKey) -> str:
        """decrypt ciphertext using a SaltedKey.

        Parameters:
            ciphertext: the encrypted message to decrypt
            salted_key: the key to use for decryption

        Raises:
            CipherNotInitializedError: if the Cipher was not initialized with an iv
        """
        cipher = Cipher(AES(salted_key.key), CBC(self.iv))
        decryptor = cipher.decryptor()
        unpadder = PKCS7(KEY_LENGTH * 8).unpadder()
        padded_text: bytes = decryptor.update(ciphertext) + decryptor.finalize()
        embedded_key_hash = padded_text[0:32]
        key_hash = hash_key(salted_key.key)
        if key_hash != embedded_key_hash:
            raise InvalidPasswordError()
        plaintext: bytes = unpadder.update(padded_text) + unpadder.finalize()
        return plaintext[32:].decode("utf-8")
