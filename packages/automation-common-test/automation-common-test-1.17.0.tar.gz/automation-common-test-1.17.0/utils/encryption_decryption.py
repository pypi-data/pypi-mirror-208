import logging
import os
from cryptography.fernet import Fernet
secret_name = 'MCMP_UI_AUTO_SECRET'


def generate_key():
    """
    Generates a key
    """
    return Fernet.generate_key()


def encrypt_password(password, secret=os.getenv(secret_name)):
    """
    Encrypts a password
    """
    encoded_password = password.encode()
    f = Fernet(secret)
    try:
        return f.encrypt(encoded_password)
    except:
        return 'Secret key is invalid'


def decrypt_password(encrypted_password, secret=os.getenv(secret_name)):
    """
    Decrypts an encrypted password
    """
    encoding = 'utf-8'
    if os.environ.get("encryption_key"):
        f = Fernet(os.environ.get("encryption_key"))
    else:
        f = Fernet(secret)
    encrypted_password = bytes(encrypted_password, encoding)
    try:
        decrypted_password = f.decrypt(encrypted_password)
        return str(decrypted_password, encoding)
    except:
        return 'Secret or Token is invalid'


def main(args):
    if args.decrypt:
        text = decrypt_password(args.text, args.secret)
    else:
        text = encrypt_password(args.text, args.secret)
    return text


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('text', help='The password or token to be encrypted or decrypted')
    parser.add_argument('-d', '--decrypt', action='store_true', help='To decrypt')
    parser.add_argument('--secret', default=os.getenv(secret_name), help='Secret key to be used for encryption')

    print(main(parser.parse_args()))
