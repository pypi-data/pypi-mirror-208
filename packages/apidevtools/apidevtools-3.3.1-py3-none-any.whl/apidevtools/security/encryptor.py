from cryptography.hazmat.primitives.ciphers.aead import AESGCM as _AESGCM
import secrets as _secrets
from typing import Any

from ..utils import evaluate as _evaluate


def randkey() -> bytes:
    return _secrets.token_bytes(32)


def encrypt(data: Any, key: bytes = randkey(), associated_data: bytes = b'') -> tuple[bytes, bytes]:
    nonce = _secrets.token_bytes(12)
    return nonce + _AESGCM(key).encrypt(nonce, str(data).encode(), associated_data), key


def decrypt(data: bytes, key: bytes, associated_data: bytes = b'', *, convert: bool = False) -> Any:
    decrypted = _AESGCM(key).decrypt(data[:12], data[12:], associated_data)
    return _evaluate(decrypted, convert)
