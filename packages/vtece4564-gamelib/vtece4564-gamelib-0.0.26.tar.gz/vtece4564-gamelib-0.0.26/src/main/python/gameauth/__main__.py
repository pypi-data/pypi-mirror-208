import argparse
import getpass
import os
import sys


from .key_util import KEY_SIZE_BITS, generate_key_pair, store_private_key, store_public_key

PRIVATE_KEY_FILENAME = "private_key.pem"
PUBLIC_KEY_FILENAME = "public_key.pem"


def _get_passphrase() -> tuple[str, str]:
    passphrase = getpass.getpass("Enter a passphrase to protect the private key: ")
    verify_passphrase = getpass.getpass("Enter the passphrase again: ")
    return passphrase, verify_passphrase


def _parse_args():
    parser = argparse.ArgumentParser(prog="gameauth-key-util")
    parser.add_argument("-o", "--output-directory", type=str, default=".", help="specify the output directory for the key files")
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    if not os.path.isdir(args.output_directory):
        print(f"{args.output_directory}: not a directory", file=sys.stderr)
        exit(1)

    private_key_path = os.path.join(args.output_directory, PRIVATE_KEY_FILENAME)
    public_key_path = os.path.join(args.output_directory, PUBLIC_KEY_FILENAME)

    if os.path.exists(private_key_path) or os.path.exists(public_key_path):
        print(f"Cannot generate keys in directory '{args.output_directory}'", file=sys.stderr)
        print(f"Files named {PRIVATE_KEY_FILENAME} and/or {PUBLIC_KEY_FILENAME} already exist in this location.",
              file=sys.stderr)
        print(f"Please choose another directory or move these files out of the way.", file=sys.stderr)
        exit(1)

    print(f"Generating a {KEY_SIZE_BITS}-bit RSA key pair")
    passphrase, verify_passphrase = _get_passphrase()
    while passphrase != verify_passphrase:
        print("Passphrase mismatch -- try again.", file=sys.stderr)
        passphrase, verify_passphrase = _get_passphrase()

    private_key, public_key = generate_key_pair()

    store_private_key(private_key, private_key_path, passphrase)
    store_public_key(public_key, public_key_path)

    print(f"Key pair successfully generated.")
