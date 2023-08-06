=========
FlashPass
=========

FlashPass is a simple cross-platform password manager written in Python.

Decrypted passwords are copied to your clipboard.

************
Installation
************

Install from PyPi:

.. code-block:: console

  pip install flashpass

Or, from the release tarball/wheel:

* Download the `latest release <https://github.com/Septem151/flashpass/releases/latest>`_
* Navigate to the directory where you saved the release
* ``pip install --upgrade [release file]``

*****
Usage
*****

Interactive mode
================

* ``flashpass``

Standard mode of FlashPass, guided prompts for password encryption/decryption.

Encrypt a new password
======================

* ``flashpass -e [name]`` or ``flashpass --encrypt [name]``

Encrypts a new password with the given name.

Decrypt an existing password
============================

* ``flashpass -d [name]`` or ``flashpass --decrypt [name]``

Decrypts an existing password with the given name and copies the password to your clipboard.

List all stored passwords
=========================

* ``flashpass -l`` or ``flashpass --list``

List the names of all stored passwords.

Print help
==========

* ``flashpass -h`` or ``flashpass --help``

Print all available commands and their descriptions.
