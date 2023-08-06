"""Exceptions module for FlashPass"""


class KeyNotInitializedError(Exception):
    """Base exception raised for errors due to accessing a key that hasn't been
    initialized yet
    """


class CipherNotInitializedError(Exception):
    """Base exception raised for errors due to accessing a cipher that
    hasn't been initialized yet"""


class SaltLengthError(Exception):
    """Exception raised for errors due to salt length not being correct.

    Parameters:
        salt: value which caused this error to be raised
        length: required salt length in bytes
    """

    def __init__(self, salt: bytes, length: int) -> None:
        super().__init__()
        self.message = (
            f"salt must be {length} bytes in length (salt length: {len(salt)})"
        )


class SaltMissingError(KeyNotInitializedError):
    """Exception raised for errors due to missing salt"""

    def __init__(self) -> None:
        super().__init__()
        self.message = "salt was None. Perhaps the key was not initialized?"


class KeyLengthError(Exception):
    """Exception raised for errors due to key length not being correct.

    Parameters:
        key: value which caused this error to be raised
        length: required key length in bytes
    """

    def __init__(self, key: bytes, length: int) -> None:
        super().__init__()
        self.message = f"key must be {length} bytes in length (key length: {len(key)})"


class KeyMissingError(KeyNotInitializedError):
    """Exception raised for errors due to missing key"""

    def __init__(self) -> None:
        super().__init__()
        self.message = "key was None. Perhaps the key was not initialized?"


class IVMissingError(CipherNotInitializedError):
    """Exception raised for errors due to missing iv"""

    def __init__(self) -> None:
        super().__init__()
        self.message = "iv was None. Perhaps the cipher was not initialized?"


class IVLengthError(Exception):
    """Exception raised for errors due to iv length not being correct.

    Parameters:
        iv: value which caused this error to be raised
        length: required iv length in bytes
    """

    def __init__(self, iv: bytes, length: int) -> None:
        super().__init__()
        self.message = f"iv must be {length} bytes in length (iv length: {len(iv)}"


class FpFileError(Exception):
    """Base exception raised for errors related to file IO"""


class FpFileWriteError(FpFileError):
    """exception raised for errors due to file writing"""


class FpFileReadError(FpFileError):
    """exception raised for errors due to file reading"""


class InvalidPasswordError(Exception):
    """exception raised for errors due to an invalid decryption password"""


class FpFileFormatError(FpFileError):
    """exception raised for errors due to a file format error"""
