"""
CHC (Contextual Hash Chain) Encryption Module
Implements blockchain-linked contextual encryption for secure cloud storage

CHANGES FROM ORIGINAL:
  1. generate_user_key() — now requires the user's hashed password as a secret
     input so the key is not derivable from public data alone.
  2. wrap_seed_for_user() / unwrap_seed_for_user() — replaced bare XOR with
     Fernet (AES-128-CBC + HMAC-SHA256) so wrapped seeds have authenticated
     encryption and are not malleable.
  3. get_or_create_owner_secret() — secrets are now persisted to
     secure_storage/key_vault/owner_secrets.json (encrypted with the system
     master key) so they survive server restarts.
"""

import os
import hmac
import hashlib
import math
import json
import base64
from typing import Dict

from cryptography.fernet import Fernet

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
BLOCK_SIZE = 32          # bytes per CHC block
_SECRETS_PATH = os.path.join("secure_storage", "key_vault", "owner_secrets.json")

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _get_system_fernet() -> Fernet:
    """
    Return a Fernet instance keyed by the system master key.
    The master key is read from secure_storage/key_vault/.master.key
    (written on first run by data_manager.KeyManager).
    """
    master_key_path = os.path.join("secure_storage", "key_vault", ".master.key")
    if not os.path.exists(master_key_path):
        raise FileNotFoundError(
            f"Master key not found at {master_key_path}. "
            "Run the application once so KeyManager can initialise it."
        )
    with open(master_key_path, "rb") as fh:
        raw = fh.read().strip()
    # raw is stored as a hex string by KeyManager
    key_bytes = bytes.fromhex(raw.decode()) if len(raw) == 64 else raw
    # Fernet needs a 32-byte URL-safe base64 key
    fernet_key = base64.urlsafe_b64encode(key_bytes[:32])
    return Fernet(fernet_key)


# ---------------------------------------------------------------------------
# Core crypto primitives (unchanged)
# ---------------------------------------------------------------------------

def hmac_sha256(key: bytes, msg: bytes) -> bytes:
    """Generate HMAC-SHA256 hash."""
    return hmac.new(key, msg, hashlib.sha256).digest()


def xor_bytes(a: bytes, b: bytes) -> bytes:
    """XOR two equal-length byte strings."""
    return bytes(x ^ y for x, y in zip(a, b))


# ---------------------------------------------------------------------------
# Seed derivation (unchanged)
# ---------------------------------------------------------------------------

def derive_seed(owner_secret: bytes, block_hash: str,
                timestamp: float, file_id: str) -> bytes:
    """
    Derive a unique 32-byte encryption seed from blockchain context.

    seed = HMAC-SHA256(owner_secret, block_hash || timestamp || file_id)
    """
    context = block_hash.encode() + str(timestamp).encode() + file_id.encode()
    seed = hmac_sha256(owner_secret, context)
    print(f"[CHC] Seed derived for file {file_id}: {seed.hex()[:16]}...")
    return seed


# ---------------------------------------------------------------------------
# CHC encrypt / decrypt (unchanged)
# ---------------------------------------------------------------------------

def encrypt_chc(plaintext: bytes, seed: bytes) -> bytes:
    """Encrypt data using the CHC algorithm."""
    state = seed
    ciphertext = b""
    blocks = math.ceil(len(plaintext) / BLOCK_SIZE)
    print(f"[CHC] Encrypting {len(plaintext)} bytes in {blocks} blocks")
    for i in range(blocks):
        start = i * BLOCK_SIZE
        end = min((i + 1) * BLOCK_SIZE, len(plaintext))
        p_block = plaintext[start:end]
        keystream = hmac_sha256(state, i.to_bytes(4, "big"))
        c_block = xor_bytes(p_block, keystream[:len(p_block)])
        ciphertext += c_block
        state = hmac_sha256(state, c_block)
    print(f"[CHC] Encryption complete: {len(ciphertext)} bytes")
    return ciphertext


def decrypt_chc(ciphertext: bytes, seed: bytes) -> bytes:
    """Decrypt data using the CHC algorithm."""
    state = seed
    plaintext = b""
    blocks = math.ceil(len(ciphertext) / BLOCK_SIZE)
    print(f"[CHC] Decrypting {len(ciphertext)} bytes in {blocks} blocks")
    for i in range(blocks):
        start = i * BLOCK_SIZE
        end = min((i + 1) * BLOCK_SIZE, len(ciphertext))
        c_block = ciphertext[start:end]
        keystream = hmac_sha256(state, i.to_bytes(4, "big"))
        p_block = xor_bytes(c_block, keystream[:len(c_block)])
        plaintext += p_block
        state = hmac_sha256(state, c_block)
    print(f"[CHC] Decryption complete: {len(plaintext)} bytes")
    return plaintext


# ---------------------------------------------------------------------------
# FIX 1 — User key derivation now requires a secret (password hash)
# ---------------------------------------------------------------------------

def generate_user_key(user_name: str, file_id: str,
                      user_password_hash: str) -> bytes:
    """
    Derive a user-specific wrapping key.

    CHANGE: A third argument `user_password_hash` (the hex PBKDF2 digest
    stored in users.json) is now required.  This makes the key unguessable
    by anyone who only knows the username and file ID.

    key = HMAC-SHA256(password_hash_bytes, username || ":" || file_id)
    """
    if not user_password_hash:
        raise ValueError("user_password_hash is required to derive a user key")
    secret = bytes.fromhex(user_password_hash)
    msg = f"{user_name}:{file_id}".encode()
    return hmac_sha256(secret, msg)


# ---------------------------------------------------------------------------
# FIX 2 — Seed wrapping uses Fernet (authenticated encryption) instead of XOR
# ---------------------------------------------------------------------------

def wrap_seed_for_user(seed: bytes, user_key: bytes) -> bytes:
    """
    Wrap the encryption seed for a specific user using Fernet.

    CHANGE: replaces bare XOR with Fernet so the wrapped seed has
    authenticated encryption (AES-128-CBC + HMAC-SHA256).  The Fernet
    token is returned as raw bytes.
    """
    fernet_key = base64.urlsafe_b64encode(user_key[:32])
    f = Fernet(fernet_key)
    token = f.encrypt(seed)          # returns bytes (URL-safe base64 token)
    return token


def unwrap_seed_for_user(wrapped_seed: bytes, user_key: bytes) -> bytes:
    """
    Unwrap the encryption seed using the user's key.

    CHANGE: mirrors wrap_seed_for_user — uses Fernet.decrypt().
    Raises cryptography.fernet.InvalidToken if the key is wrong or the
    token has been tampered with.
    """
    fernet_key = base64.urlsafe_b64encode(user_key[:32])
    f = Fernet(fernet_key)
    seed = f.decrypt(wrapped_seed)   # raises InvalidToken on bad key/tamper
    return seed


# ---------------------------------------------------------------------------
# File ID generation (unchanged)
# ---------------------------------------------------------------------------

def generate_file_id(filename: str, owner: str) -> str:
    """Generate a unique file ID."""
    import time
    timestamp = str(time.time())
    data = f"{filename}:{owner}:{timestamp}".encode()
    return "file_" + hashlib.sha256(data).hexdigest()[:12]


# ---------------------------------------------------------------------------
# FIX 3 — Owner secrets are persisted so they survive restarts
# ---------------------------------------------------------------------------

# In-memory cache; populated lazily from disk
_owner_secrets_cache: Dict[str, bytes] = {}


def _load_owner_secrets() -> Dict[str, bytes]:
    """Load and decrypt owner secrets from disk into the cache."""
    if not os.path.exists(_SECRETS_PATH):
        return {}
    try:
        f = _get_system_fernet()
        with open(_SECRETS_PATH, "rb") as fh:
            encrypted_blob = fh.read()
        decrypted = f.decrypt(encrypted_blob)
        raw: Dict[str, str] = json.loads(decrypted.decode())
        return {owner: bytes.fromhex(secret_hex)
                for owner, secret_hex in raw.items()}
    except Exception as exc:
        print(f"[CHC] WARNING: could not load owner secrets: {exc}")
        return {}


def _save_owner_secrets(secrets: Dict[str, bytes]) -> None:
    """Encrypt and persist owner secrets to disk."""
    os.makedirs(os.path.dirname(_SECRETS_PATH), exist_ok=True)
    try:
        f = _get_system_fernet()
        raw = {owner: secret.hex() for owner, secret in secrets.items()}
        blob = json.dumps(raw).encode()
        encrypted_blob = f.encrypt(blob)
        with open(_SECRETS_PATH, "wb") as fh:
            fh.write(encrypted_blob)
    except Exception as exc:
        print(f"[CHC] WARNING: could not persist owner secrets: {exc}")


def get_or_create_owner_secret(owner: str) -> bytes:
    """
    Return the owner's master secret, creating and persisting one if needed.

    CHANGE: secrets are now loaded from / saved to an encrypted JSON file on
    disk so they survive server restarts.  The file is encrypted with the
    system Fernet key from KeyManager.
    """
    global _owner_secrets_cache

    # Populate cache from disk on first call
    if not _owner_secrets_cache:
        _owner_secrets_cache = _load_owner_secrets()

    if owner not in _owner_secrets_cache:
        _owner_secrets_cache[owner] = os.urandom(32)
        print(f"[CHC] Generated new master secret for owner: {owner}")
        _save_owner_secrets(_owner_secrets_cache)

    return _owner_secrets_cache[owner]
