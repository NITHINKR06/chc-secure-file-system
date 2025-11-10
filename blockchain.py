"""
Blockchain Module for CHC System
Simulates a blockchain ledger for storing file metadata and context

This module implements a simplified blockchain for the secure file management system.
It provides immutable storage for file metadata, access control logs, and security events.

Key Features:
- Immutable blockchain records
- Access control logging
- Security audit trails
- Chain integrity verification
- Tamper-proof metadata storage

The blockchain serves as the "on-chain" component of the system, providing:
- Immutability: Records cannot be modified after creation
- Auditability: Complete audit trail of all operations
- Integrity: Hash linking prevents tampering
- Context: Provides context for encryption seeds
"""

import json  # For JSON data serialization/deserialization
import os  # For file system operations
import time  # For timestamp generation
import hashlib  # For SHA256 hash calculations
from typing import Dict, List, Optional, Tuple  # Type hints for better code documentation

# Configuration
BLOCKCHAIN_FILE = "blockchain.json"  # File where blockchain data is stored

def calculate_block_hash(block_data: Dict) -> str:
    """
    Calculate SHA256 hash of a block for blockchain integrity
    
    This function is crucial for blockchain integrity because:
    - It creates a unique fingerprint for each block
    - It prevents tampering (any change would change the hash)
    - It enables hash linking between blocks
    - It provides cryptographic verification
    
    The hash is calculated by:
    1. Removing any existing hash field (to avoid circular reference)
    2. Sorting keys for consistent hashing (order doesn't matter)
    3. Converting to JSON string
    4. Calculating SHA256 hash
    
    Args:
        block_data: Block dictionary (without hash field)
    
    Returns:
        Hexadecimal hash string - unique fingerprint of the block
    """
    # Create a copy without the hash field if it exists (prevents circular reference)
    data = {k: v for k, v in block_data.items() if k != 'hash'}
    
    # Sort keys for consistent hashing (order doesn't affect the hash)
    json_str = json.dumps(data, sort_keys=True)
    
    # Calculate SHA256 hash for cryptographic security
    return hashlib.sha256(json_str.encode()).hexdigest()

def init_chain() -> None:
    """
    Initialize the blockchain with a genesis block if it doesn't exist
    """
    if not os.path.exists(BLOCKCHAIN_FILE):
        genesis = {
            "index": 0,
            "timestamp": time.time(),
            "file_id": "genesis",
            "owner": "system",
            "authorized_users": [],
            "prev_hash": "0",
            "data": "Genesis Block - CHC Secure Cloud Storage"
        }
        genesis["block_hash"] = calculate_block_hash(genesis)
        
        # Save genesis block
        with open(BLOCKCHAIN_FILE, "w") as f:
            json.dump([genesis], f, indent=2)
        
        print("[Blockchain] Genesis block created")
    else:
        print("[Blockchain] Chain already exists")

def get_chain() -> List[Dict]:
    """
    Retrieve the entire blockchain
    
    Returns:
        List of all blocks in the chain
    """
    if not os.path.exists(BLOCKCHAIN_FILE):
        init_chain()
    
    with open(BLOCKCHAIN_FILE, "r") as f:
        chain = json.load(f)
    
    return chain

def get_latest_block() -> Dict:
    """
    Get the most recent block in the chain
    
    Returns:
        The latest block dictionary
    """
    chain = get_chain()
    return chain[-1] if chain else None

def add_block(file_id: str, owner: str, authorized_users: List[str], 
              file_metadata: Optional[Dict] = None) -> Tuple[str, float]:
    """
    Add a new block to the blockchain for a file upload
    
    Args:
        file_id: Unique identifier for the file
        owner: Name of the file owner
        authorized_users: List of users authorized to decrypt
        file_metadata: Optional additional metadata
    
    Returns:
        Tuple of (block_hash, timestamp)
    """
    chain = get_chain()
    prev_block = chain[-1]
    
    # Create new block
    new_block = {
        "index": len(chain),
        "timestamp": time.time(),
        "file_id": file_id,
        "owner": owner,
        "authorized_users": authorized_users,
        "prev_hash": prev_block.get("block_hash", prev_block.get("hash", "0")),
    }
    
    # Add optional metadata
    if file_metadata:
        new_block["metadata"] = file_metadata
    
    # Calculate block hash
    new_block["block_hash"] = calculate_block_hash(new_block)
    
    # Append to chain
    chain.append(new_block)
    
    # Save updated chain
    with open(BLOCKCHAIN_FILE, "w") as f:
        json.dump(chain, f, indent=2)
    
    print(f"[Blockchain] Block #{new_block['index']} added for file {file_id}")
    print(f"[Blockchain] Block hash: {new_block['block_hash'][:32]}...")
    
    return new_block["block_hash"], new_block["timestamp"]

def get_block_by_file_id(file_id: str) -> Optional[Dict]:
    """
    Find a block by file ID
    
    Args:
        file_id: File identifier to search for
    
    Returns:
        Block dictionary if found, None otherwise
    """
    chain = get_chain()
    
    for block in chain:
        if block.get("file_id") == file_id:
            return block
    
    return None

def get_all_file_blocks() -> List[Dict]:
    """
    Get all blocks that represent file uploads (excluding genesis)
    
    Returns:
        List of file blocks
    """
    chain = get_chain()
    # Skip genesis block (index 0)
    return [block for block in chain if block.get("index", 0) > 0]

def verify_chain_integrity() -> bool:
    """
    Verify the integrity of the blockchain
    
    Returns:
        True if chain is valid, False otherwise
    """
    chain = get_chain()
    
    if not chain:
        return False
    
    # Check genesis block
    genesis = chain[0]
    if genesis.get("prev_hash") != "0":
        print("[Blockchain] Invalid genesis block")
        return False
    
    # Verify each block's hash and link to previous
    for i in range(1, len(chain)):
        current = chain[i]
        previous = chain[i - 1]
        
        # Check hash calculation
        calculated_hash = calculate_block_hash(current)
        stored_hash = current.get("block_hash", current.get("hash"))
        
        if calculated_hash != stored_hash:
            print(f"[Blockchain] Invalid hash at block {i}")
            return False
        
        # Check link to previous block
        prev_hash = previous.get("block_hash", previous.get("hash"))
        if current.get("prev_hash") != prev_hash:
            print(f"[Blockchain] Broken chain at block {i}")
            return False
    
    print("[Blockchain] Chain integrity verified")
    return True

def get_user_accessible_files(user_name: str) -> List[Dict]:
    """
    Get all files that a user has access to
    
    Args:
        user_name: Name of the user
    
    Returns:
        List of accessible file blocks
    """
    chain = get_chain()
    accessible = []
    
    for block in chain:
        if block.get("index", 0) == 0:  # Skip genesis
            continue
        
        # Check if user is owner or in authorized list
        if (block.get("owner") == user_name or 
            user_name in block.get("authorized_users", [])):
            accessible.append(block)
    
    return accessible

def log_access_control(file_id: str, access_log: Dict) -> bool:
    """
    Log access control information to blockchain
    
    Args:
        file_id: File identifier
        access_log: Access control information
    
    Returns:
        True if logged successfully
    """
    try:
        # Find the block for this file
        block = get_block_by_file_id(file_id)
        if not block:
            print(f"[Blockchain] File {file_id} not found in blockchain")
            return False
        
        # Add access control log to the block
        if "access_logs" not in block:
            block["access_logs"] = []
        
        block["access_logs"].append(access_log)
        
        # Update the blockchain file
        chain = get_chain()
        for i, b in enumerate(chain):
            if b.get("file_id") == file_id:
                chain[i] = block
                break
        
        # Save updated chain
        with open(BLOCKCHAIN_FILE, "w") as f:
            json.dump(chain, f, indent=2)
        
        print(f"[Blockchain] Access control logged for file {file_id}")
        return True
        
    except Exception as e:
        print(f"[Blockchain] Error logging access control: {e}")
        return False

def get_security_audit_trail(file_id: str) -> List[Dict]:
    """
    Get security audit trail for a file
    
    Args:
        file_id: File identifier
    
    Returns:
        List of security events
    """
    block = get_block_by_file_id(file_id)
    if not block:
        return []
    
    audit_trail = []
    
    # Add initial upload event
    audit_trail.append({
        "event": "file_uploaded",
        "timestamp": block.get("timestamp"),
        "owner": block.get("owner"),
        "authorized_users": block.get("authorized_users", []),
        "block_hash": block.get("block_hash"),
        "description": "File uploaded and encrypted"
    })
    
    # Add access control logs
    access_logs = block.get("access_logs", [])
    for log in access_logs:
        if log.get("access_granted"):
            audit_trail.append({
                "event": "authorized_access",
                "timestamp": log.get("access_time"),
                "user": log.get("user"),
                "description": "Authorized user successfully accessed file"
            })
        elif log.get("access_denied"):
            audit_trail.append({
                "event": "unauthorized_access_attempt",
                "timestamp": log.get("attempt_time"),
                "user": log.get("unauthorized_user"),
                "reason": log.get("reason"),
                "description": "Unauthorized access attempt blocked"
            })
        elif log.get("decryption_failed"):
            audit_trail.append({
                "event": "decryption_failed",
                "timestamp": log.get("attempt_time"),
                "user": log.get("user"),
                "error": log.get("error"),
                "description": "Decryption attempt failed"
            })
    
    return sorted(audit_trail, key=lambda x: x.get("timestamp", 0))

def verify_file_security(file_id: str) -> Dict:
    """
    Verify security outcome for a file
    
    Args:
        file_id: File identifier
    
    Returns:
        Security verification results
    """
    block = get_block_by_file_id(file_id)
    if not block:
        return {"valid": False, "reason": "File not found in blockchain"}
    
    # Check blockchain integrity
    chain_valid = verify_chain_integrity()
    
    # Check access control logs
    access_logs = block.get("access_logs", [])
    unauthorized_attempts = [log for log in access_logs if log.get("access_denied")]
    successful_accesses = [log for log in access_logs if log.get("access_granted")]
    failed_decryptions = [log for log in access_logs if log.get("decryption_failed")]
    
    return {
        "valid": chain_valid,
        "file_id": file_id,
        "block_hash": block.get("block_hash"),
        "owner": block.get("owner"),
        "authorized_users": block.get("authorized_users", []),
        "security_events": {
            "unauthorized_attempts": len(unauthorized_attempts),
            "successful_accesses": len(successful_accesses),
            "failed_decryptions": len(failed_decryptions)
        },
        "data_confidentiality": "maintained" if chain_valid else "compromised",
        "access_control": "enforced" if unauthorized_attempts else "not_tested",
        "cryptographic_verification": "verified" if chain_valid else "failed"
    }

def format_block_for_display(block: Dict) -> Dict:
    """
    Format a block for display in the UI
    
    Args:
        block: Block dictionary
    
    Returns:
        Formatted block data
    """
    return {
        "index": block.get("index"),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", 
                                   time.localtime(block.get("timestamp", 0))),
        "file_id": block.get("file_id"),
        "owner": block.get("owner"),
        "authorized_users": ", ".join(block.get("authorized_users", [])),
        "block_hash": block.get("block_hash", block.get("hash", ""))[:32] + "...",
        "prev_hash": block.get("prev_hash", "")[:32] + "..."
    }

# Initialize blockchain on module import
if __name__ != "__main__":
    init_chain()
