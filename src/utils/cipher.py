import os
import hashlib
from dotenv import load_dotenv

load_dotenv()

PRIVATE_KEY = os.getenv("PRIVATE_KEY")
if not PRIVATE_KEY:
    raise ValueError("PRIVATE_KEY not set in .env")

def _stretch_key(key: str, length: int) -> bytes:
  
    hash_obj = hashlib.sha256(key.encode())
    stretched = hash_obj.digest()
    while len(stretched) < length:
        hash_obj = hashlib.sha256(stretched)
        stretched += hash_obj.digest()
    return stretched[:length]

def encrypt(text: str) -> str:
    text_bytes = text.encode('utf-8')
    key_bytes = _stretch_key(PRIVATE_KEY, len(text_bytes))
    encrypted_bytes = bytes([b ^ k for b, k in zip(text_bytes, key_bytes)])
    return encrypted_bytes.hex()

def decrypt(hash_str: str) -> str:
    encrypted_bytes = bytes.fromhex(hash_str)
    key_bytes = _stretch_key(PRIVATE_KEY, len(encrypted_bytes))
    decrypted_bytes = bytes([b ^ k for b, k in zip(encrypted_bytes, key_bytes)])
    return decrypted_bytes.decode('utf-8')

if __name__ == "__main__":
    secret = "Hello, this is a test message!"
    encrypted = encrypt(secret)
    print("Encrypted:", encrypted)

    decrypted = decrypt(encrypted)
    print("Decrypted:", decrypted)
