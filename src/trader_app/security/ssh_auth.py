import os
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
import base64
from datetime import datetime

KEY_DIR = os.path.expanduser("~/.traderapp_keys")
PRIVATE_KEY_PATH = os.path.join(KEY_DIR, "id_rsa")
PUBLIC_KEY_PATH = os.path.join(KEY_DIR, "id_rsa.pub")
REGISTERED_PUBKEY_PATH = os.path.join(KEY_DIR, "registered_pubkey.pub")


def generate_key_pair():
    """
    Generate a new RSA key pair and save to ~/.traderapp_keys.
    """
    os.makedirs(KEY_DIR, exist_ok=True)
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=4096
    )
    with open(PRIVATE_KEY_PATH, "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))
    public_key = private_key.public_key()
    with open(PUBLIC_KEY_PATH, "wb") as f:
        f.write(public_key.public_bytes(
            encoding=serialization.Encoding.OpenSSH,
            format=serialization.PublicFormat.OpenSSH
        ))
    print(f"Private key saved to {PRIVATE_KEY_PATH}")
    print(f"Public key saved to {PUBLIC_KEY_PATH}")


def register_public_key():
    """
    Simulate registering the public key in the app DB (save to a local file for now).
    """
    with open(PUBLIC_KEY_PATH, "rb") as f:
        pubkey = f.read()
    with open(REGISTERED_PUBKEY_PATH, "wb") as f:
        f.write(pubkey)
    print(f"Registered public key saved to {REGISTERED_PUBKEY_PATH}")


def sign_message(message: bytes) -> str:
    """
    Sign a message with the private key. Returns base64 signature.
    """
    with open(PRIVATE_KEY_PATH, "rb") as f:
        private_key = serialization.load_pem_private_key(f.read(), password=None)
    signature = private_key.sign(
        message,
        padding.PKCS1v15(),
        hashes.SHA256()
    )
    return base64.b64encode(signature).decode()


def verify_signature(message: bytes, signature_b64: str) -> bool:
    """
    Verify a base64 signature using the registered public key.
    """
    with open(REGISTERED_PUBKEY_PATH, "rb") as f:
        public_key = serialization.load_ssh_public_key(f.read())
    signature = base64.b64decode(signature_b64)
    try:
        public_key.verify(
            signature,
            message,
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        return True
    except Exception:
        return False


def get_timestamp_message() -> bytes:
    """
    Return a timestamped message for signing (prevents replay attacks).
    """
    now = datetime.utcnow().isoformat() + "Z"
    return f"timestamp:{now}".encode()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="SSH Key Auth Utility")
    parser.add_argument("command", choices=["generate", "register", "sign", "verify"], help="Command to run")
    parser.add_argument("--message", help="Message to sign/verify")
    parser.add_argument("--signature", help="Signature to verify (base64)")
    args = parser.parse_args()
    if args.command == "generate":
        generate_key_pair()
    elif args.command == "register":
        register_public_key()
    elif args.command == "sign":
        msg = args.message.encode() if args.message else get_timestamp_message()
        sig = sign_message(msg)
        print(f"Signature: {sig}")
    elif args.command == "verify":
        if not args.signature:
            print("--signature required for verify")
        else:
            msg = args.message.encode() if args.message else get_timestamp_message()
            ok = verify_signature(msg, args.signature)
            print(f"Valid: {ok}") 