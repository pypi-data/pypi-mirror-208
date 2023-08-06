"""CLI Module for FlashPass"""
import argparse
import getpass
import sys
import typing as t

import pyperclip

from flashpass import __version__
from flashpass.exceptions import InvalidPasswordError
from flashpass.io import FpFile, all_files

MAX_ATTEMPTS = 3


def _validate_filename(filename: t.Optional[str]) -> FpFile:
    if filename is None:
        filename = input("Filename: ")
    filename = filename.strip()
    if len(filename) == 0:
        sys.exit("Filename cannot be empty")
    if filename.startswith("-") or any(
        c in filename
        for c in (
            "\0",
            "/",
            "\\",
            "?",
            "%",
            "*",
            ":",
            "|",
            '"',
            "<",
            ">",
            ".",
            ";",
            "=",
            " ",
        )
    ):
        sys.exit("Invalid filename")
    return FpFile(f"{filename}.fp")


def run_encrypt(pw_file: FpFile) -> None:
    """Runs flashpass in encrypt mode.

    Args:
        pw_file (FpFile): The file to operate on.
    """
    if pw_file.exists():
        sys.exit("Cannot encrypt an already existing file.")
    match = False
    while not match:
        stored_pw = getpass.getpass("Enter password to store: ")
        if len(stored_pw) == 0:
            print("Password cannot be empty.")
            continue
        match = stored_pw == getpass.getpass("Verify password to store: ")
        if not match:
            print("Password didn't match.")
    match = False
    while not match:
        file_pw = getpass.getpass("Enter encryption password: ")
        if len(file_pw) == 0:
            print("Password cannot be empty.")
            continue
        match = file_pw == getpass.getpass("Verify encryption password: ")
        if not match:
            print("Password didn't match.")
    pw_file.write(stored_pw, file_pw)
    print("Password stored successfully!")


def run_decrypt(pw_file: FpFile) -> None:
    """Runs flashpass in decrypt mode.

    Args:
        pw_file (FpFile): The file to operate on.
    """
    if not pw_file.exists():
        sys.exit("No password found for the given filename.")
    attempts = MAX_ATTEMPTS
    while attempts > 0:
        file_pw = getpass.getpass("Enter decryption password: ")
        try:
            stored_pw = pw_file.read(file_pw)
            pyperclip.copy(stored_pw)
            print("Password copied to clipboard.")
            return
        except InvalidPasswordError:
            attempts -= 1
            print(f"Invalid password (attempts remaining: {attempts})")
    if attempts == 0:
        sys.exit("Unable to decrypt password file.")


def run_interactive(pw_file: t.Optional[FpFile] = None) -> None:
    """Runs flashpass in interactive mode.

    Args:
        pw_file (FpFile, optional): The file to operate on. Defaults to None.
    """
    if pw_file is not None:
        if pw_file.exists():
            run_decrypt(pw_file)
        else:
            run_encrypt(pw_file)
        return
    while True:
        mode = input(
            "[E]ncrypt a new file or [D]ecrypt an existing file? [E/d]: "
        ).lower()
        if mode not in ("e", "d", ""):
            print(f'"{mode}" is not an option, try again.')
            continue
        break
    filename = input("Filename: ")
    pw_file = _validate_filename(filename)
    if mode in ("e", ""):
        run_encrypt(pw_file)
    else:
        run_decrypt(pw_file)


def main() -> None:
    """Main flashpass entrypoint."""
    parser = argparse.ArgumentParser(
        "flashpass", description="Encrypt & Decrypt FlashPass .fp files"
    )
    parser.add_argument(
        "-v", "--version", action="version", version=f"%(prog)s {__version__}"
    )
    parser.add_argument("filename", type=str, nargs="?", help="password to operate on")
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument(
        "-e", "--encrypt", action="store_true", help="encrypt a new password"
    )
    group.add_argument(
        "-d", "--decrypt", action="store_true", help="decrypt an existing password"
    )
    group.add_argument(
        "-l", "--list", action="store_true", help="list all stored passwords"
    )
    args = parser.parse_args()
    list_mode: bool = args.list
    if list_mode:
        print(*all_files(), sep="\n")
        return
    filename: t.Optional[str] = args.filename
    encrypt_mode: bool = args.encrypt
    decrypt_mode: bool = args.decrypt
    try:
        if filename is None:
            run_interactive()
        else:
            pw_file = _validate_filename(filename)
            if encrypt_mode:
                run_encrypt(pw_file)
            elif decrypt_mode:
                run_decrypt(pw_file)
            else:
                run_interactive(pw_file)
    except (EOFError, KeyboardInterrupt):
        print()
        sys.exit(2)


if __name__ == "__main__":
    main()
