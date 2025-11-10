"""
CHC (Contextual Hash Chain) Encryption Module
Implements blockchain-linked contextual encryption for secure cloud storage

This module provides the core encryption functionality for the secure file management system.
It implements the CHC algorithm which provides forward security through state chaining,
ensuring that each block's encryption depends on the previous ciphertext blocks.

Key Features:
- Contextual seed derivation from blockchain context
- CHC encryption with forward security
- User-specific key management
- Secure seed wrapping/unwrapping
"""

import os  # For generating random bytes and file operations
import hmac  # For HMAC-SHA256 cryptographic operations
import hashlib  # For SHA256 hash functions
import math  # For mathematical operations (ceil function)
from typing import Tuple, Dict  # Type hints for better code documentation

# Configuration constants
BLOCK_SIZE = 32  # bytes per block for CHC encryption - 32 bytes provides good security and performance

def hmac_sha256(key: bytes, msg: bytes) -> bytes:
    """
    Generate HMAC-SHA256 hash for cryptographic operations
    
    HMAC (Hash-based Message Authentication Code) provides:
    - Authentication: Verifies data hasn't been tampered with
    - Integrity: Ensures data hasn't been modified
    - Security: Cryptographically secure hash function
    
    Args:
        key: The secret key for HMAC
        msg: The message to hash
    Returns:
        32-byte HMAC-SHA256 hash
    """
    return hmac.new(key, msg, hashlib.sha256).digest()

def xor_bytes(a: bytes, b: bytes) -> bytes:
    """
    XOR two byte strings for encryption operations
    
    XOR is used in the CHC algorithm for:
    - Encrypting plaintext with keystream
    - Wrapping/unwrapping seeds for users
    - Providing reversible encryption operations
    
    Args:
        a: First byte string
        b: Second byte string
    Returns:
        XOR result of the two byte strings
    """
    return bytes(x ^ y for x, y in zip(a, b))

def derive_seed(owner_secret: bytes, block_hash: str, timestamp: float, file_id: str) -> bytes:
    """
    Derive a unique seed from blockchain context and owner secret
    
    This is the core of the contextual encryption system. The seed is derived from:
    - Owner's master secret (provides ownership control)
    - Blockchain block hash (provides immutability and context)
    - Timestamp (provides uniqueness and temporal context)
    - File ID (provides file-specific context)
    
    This ensures that:
    - Each file gets a unique encryption seed
    - The seed is tied to blockchain context (tamper-proof)
    - Only the owner can derive the seed
    - The seed cannot be guessed or brute-forced
    
    Args:
        owner_secret: Owner's master secret (32 bytes) - provides ownership control
        block_hash: Hash of the blockchain block - provides immutability
        timestamp: Block timestamp - provides temporal uniqueness
        file_id: Unique file identifier - provides file-specific context
    
    Returns:
        32-byte seed for encryption - unique for this file and context
    """
    # Combine all context elements to create unique context
    context = block_hash.encode() + str(timestamp).encode() + file_id.encode()
    
    # Generate seed using HMAC-SHA256 for cryptographic security
    seed = hmac_sha256(owner_secret, context)
    print(f"[CHC] Seed derived for file {file_id}: {seed.hex()[:16]}...")
    return seed

def encrypt_chc(plaintext: bytes, seed: bytes) -> bytes:
    """
    Encrypt data using CHC (Contextual Hash Chain) algorithm
    
    The CHC algorithm:
    1. Divides plaintext into blocks
    2. For each block:
       - Generates keystream from current state
       - XORs plaintext with keystream
       - Updates state using ciphertext block
    
    Args:
        plaintext: Data to encrypt
        seed: 32-byte encryption seed
    
    Returns:
        Encrypted ciphertext
    """
    state = seed
    ciphertext = b""
    blocks = math.ceil(len(plaintext) / BLOCK_SIZE)
    
    print(f"[CHC] Encrypting {len(plaintext)} bytes in {blocks} blocks")
    
    for i in range(blocks):
        # Get current block
        start = i * BLOCK_SIZE
        end = min((i + 1) * BLOCK_SIZE, len(plaintext))
        p_block = plaintext[start:end]
        
        # Generate keystream for this block
        keystream = hmac_sha256(state, i.to_bytes(4, "big"))
        
        # Encrypt block
        c_block = xor_bytes(p_block, keystream[:len(p_block)])
        ciphertext += c_block
        
        # Update state with ciphertext block (forward security)
        state = hmac_sha256(state, c_block)
    
    print(f"[CHC] Encryption complete: {len(ciphertext)} bytes")
    return ciphertext

def decrypt_chc(ciphertext: bytes, seed: bytes) -> bytes:
    """
    Decrypt data using CHC algorithm
    
    Args:
        ciphertext: Encrypted data
        seed: 32-byte decryption seed
    
    Returns:
        Decrypted plaintext
    """
    state = seed
    plaintext = b""
    blocks = math.ceil(len(ciphertext) / BLOCK_SIZE)
    
    print(f"[CHC] Decrypting {len(ciphertext)} bytes in {blocks} blocks")
    
    for i in range(blocks):
        # Get current block
        start = i * BLOCK_SIZE
        end = min((i + 1) * BLOCK_SIZE, len(ciphertext))
        c_block = ciphertext[start:end]
        
        # Generate keystream for this block
        keystream = hmac_sha256(state, i.to_bytes(4, "big"))
        
        # Decrypt block
        p_block = xor_bytes(c_block, keystream[:len(c_block)])
        plaintext += p_block
        
        # Update state with ciphertext block
        state = hmac_sha256(state, c_block)
    
    print(f"[CHC] Decryption complete: {len(plaintext)} bytes")
    return plaintext

def generate_user_key(user_name: str, file_id: str) -> bytes:
    """
    Generate a user-specific key for seed wrapping
    
    Args:
        user_name: Name of the user
        file_id: File identifier
    
    Returns:
        32-byte user key
    """
    # Simple key derivation from user name and file ID
    # In production, this would use proper key management
    data = f"{user_name}:{file_id}".encode()
    return hashlib.sha256(data).digest()

def wrap_seed_for_user(seed: bytes, user_key: bytes) -> bytes:
    """
    Wrap the encryption seed for a specific user
    
    Args:
        seed: Master encryption seed
        user_key: User's key
    
    Returns:
        Wrapped seed
    """
    # XOR-based wrapping (simplified for demo)
    wrapped = xor_bytes(seed, user_key)
    return wrapped

def unwrap_seed_for_user(wrapped_seed: bytes, user_key: bytes) -> bytes:
    """
    Unwrap the encryption seed using user's key
    
    Args:
        wrapped_seed: Wrapped seed
        user_key: User's key
    
    Returns:
        Original seed
    """
    # XOR-based unwrapping
    seed = xor_bytes(wrapped_seed, user_key)
    return seed

def generate_file_id(filename: str, owner: str) -> str:
    """
    Generate a unique file ID
    
    Args:
        filename: Original filename
        owner: Owner name
    
    Returns:
        Unique file ID
    """
    import time
    timestamp = str(time.time())
    data = f"{filename}:{owner}:{timestamp}".encode()
    hash_val = hashlib.sha256(data).hexdigest()
    return f"file_{hash_val[:12]}"

# Storage for owner secrets (in production, use secure key storage)
owner_secrets: Dict[str, bytes] = {}

def get_or_create_owner_secret(owner: str) -> bytes:
    """
    Get or create an owner's master secret
    
    Args:
        owner: Owner name
    
    Returns:
        32-byte master secret
    """
    if owner not in owner_secrets:
        # Generate new secret for this owner
        owner_secrets[owner] = os.urandom(32)
        print(f"[CHC] Generated new master secret for owner: {owner}")
    return owner_secrets[owner]
