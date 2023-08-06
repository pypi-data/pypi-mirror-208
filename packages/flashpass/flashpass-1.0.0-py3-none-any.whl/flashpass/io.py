"""IO Module for FlashPass"""
import os
import sys
import typing as t
from pathlib import Path

from flashpass.crypto import (
    HASH_LENGTH,
    IV_LENGTH,
    SALT_LENGTH,
    FpCipher,
    SaltedKey,
    gen_key,
    hash_key,
)
from flashpass.exceptions import FpFileFormatError, FpFileReadError, FpFileWriteError


def _get_storage_dir() -> Path:
    platform = sys.platform
    if platform.startswith("linux") or platform.startswith("freebsd"):
        return Path.home() / ".local" / "share" / "flashpass"
    if platform.startswith("win") or platform.startswith("cygwin"):
        appdata_dir = os.getenv("LOCALAPPDATA")
        if appdata_dir is None:
            return Path.home() / "AppData" / "Local" / "flashpass"
        return Path(appdata_dir) / "flashpass"
    if platform.startswith("darwin"):
        return Path.home() / "Library" / "Application Support" / "flashpass"
    return Path.home() / ".flashpass"


STORAGE_DIR = _get_storage_dir()
MIN_FILESIZE = IV_LENGTH + SALT_LENGTH + HASH_LENGTH + 16


def all_files() -> t.List[str]:
    """List of .fp files present in the storage directory.

    Returns:
        list: .fp files sorted in ascending order
    """
    filenames: t.List[str] = []
    for file in STORAGE_DIR.iterdir():
        if len(file.suffixes) == 1 and file.suffix == ".fp":
            filenames.append(file.stem)
    filenames.sort()
    return filenames


class FpFile:
    """An FpFile reader and writer.

    Parameters:
        filename: the filename
    """

    def __init__(self, filename: str) -> None:
        self._filepath = STORAGE_DIR / filename
        self._filename = filename

    def exists(self) -> bool:
        """Returns whether the FpFile exists.

        Returns:
            True if the file exists, False if not.
        """
        return self._filepath.exists()

    def write(self, stored_password: str, encryption_password: str) -> None:
        """encrypts a password and writes to an .fp file.

        Parameters:
            salted_key: the salted key to use for encryption/decryption
            fp_cipher: the cipher to use for encryption/decryption
        """
        if not STORAGE_DIR.exists():
            STORAGE_DIR.mkdir(parents=True)
        if self.exists():
            raise FpFileWriteError()
        salted_key = SaltedKey(encryption_password)
        fp_cipher = FpCipher()
        key_hash = hash_key(salted_key.key)
        plaintext = key_hash + stored_password.encode("utf-8")
        ciphertext = fp_cipher.encrypt_message(plaintext, salted_key)
        with open(self._filepath, "wb") as file:
            file.write(_encode_byte_val(salted_key.salt))
            file.write(_encode_byte_val(fp_cipher.iv))
            file.write(_encode_byte_val(ciphertext))

    def read(self, password: str) -> str:
        """decrypts an .fp file with the given password.

        Parameters:
            password: the password to decrypt the file

        Returns:
            str: the decrypted file contents

        Raises:
            FpFileReadError: if the file did not exist
            FpFileFormatError: if the file was not long enough
            InvalidPasswordError: if the password was not able to decrypt the file
        """
        if not self.exists():
            raise FpFileReadError()
        if self._filepath.stat().st_size < MIN_FILESIZE:
            raise FpFileFormatError()
        with open(self._filepath, "rb") as file:
            salt_len = int.from_bytes(file.read(4), "big")
            salt = file.read(salt_len)
            decrypt_key = gen_key(password, salt)
            salted_key = SaltedKey.from_bytes(decrypt_key, salt)
            iv_len = int.from_bytes(file.read(4), "big")
            iv = file.read(iv_len)  # pylint: disable=invalid-name
            ciphertext_len = int.from_bytes(file.read(4), "big")
            ciphertext = file.read(ciphertext_len)
            fp_cipher = FpCipher(iv)
            plaintext = fp_cipher.decrypt_message(ciphertext, salted_key)
        return plaintext


def _encode_byte_val(value: bytes) -> bytes:
    """len(value) + value"""
    return len(value).to_bytes(4, "big") + value
