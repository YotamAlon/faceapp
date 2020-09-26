#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import getpass
from cryptography.fernet import Fernet
import base64
ENCRYPTED_KEY = b'gAAAAABfbxPt-pX7yF51b9PYMF9dcSVUct2wum1bAWv95QueRAexxCfrF3M0xRbwn91_EvrlKCeR1-l5Or8RdmyaNU1ef0ccWyq' \
                b'3U1TF-Rd7qRm64ZjeI7LP69ggjggpTm2O-4P9lrUP'


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'face.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    if sys.argv[1] == 'runserver' and not os.environ.get('AZURE_KEY', None):
        password = getpass.getpass(prompt='Enter decryption password: ')
        f = Fernet(base64.urlsafe_b64encode(password.encode().zfill(32)))
        os.environ['AZURE_KEY'] = f.decrypt(ENCRYPTED_KEY).decode()

    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
