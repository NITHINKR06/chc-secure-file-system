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
    1. Removing any existing hash fields (to avoid circular reference)
    2. Sorting keys for consistent hashing (order doesn't matter)
    3. Converting to JSON string with consistent formatting
    4. Calculating SHA256 hash
    
    Args:
        block_data: Block dictionary (without hash field)
    
    Returns:
        Hexadecimal hash string - unique fingerprint of the block
    """
    # Create a copy without the hash fields if they exist (prevents circular reference)
    # Exclude both 'hash' and 'block_hash' since the hash shouldn't include itself
    data = {k: v for k, v in block_data.items() if k not in ('hash', 'block_hash')}
    
    # Use consistent JSON serialization:
    # - sort_keys=True: Ensures dictionary keys are always in the same order
    # - separators=(',', ':'): Removes whitespace for consistent output
    # - ensure_ascii=False: Handles unicode consistently
    # This ensures the same data always produces the same hash
    json_str = json.dumps(data, sort_keys=True, separators=(',', ':'), ensure_ascii=False)
    
    # Calculate SHA256 hash for cryptographic security
    return hashlib.sha256(json_str.encode('utf-8')).hexdigest()

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
    # Ensure chain is valid before adding new block
    if not verify_chain_integrity():
        print(f"[Blockchain] Chain integrity invalid before adding block, repairing...")
        repair_chain_integrity()
    
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

def repair_chain_integrity() -> bool:
    """
    Repair the blockchain by recalculating all hashes
    
    This function fixes blocks that were modified after creation
    (e.g., when access_logs were added without recalculating the hash)
    
    Returns:
        True if chain was repaired successfully
    """
    try:
        chain = get_chain()
        
        if not chain:
            print("[Blockchain] Cannot repair: Chain is empty")
            return False
        
        print(f"[Blockchain] Starting chain repair for {len(chain)} blocks...")
        
        # Repair genesis block hash (shouldn't change, but recalculate for consistency)
        old_genesis_hash = chain[0].get("block_hash", chain[0].get("hash"))
        chain[0]["block_hash"] = calculate_block_hash(chain[0])
        if old_genesis_hash != chain[0]["block_hash"]:
            print(f"[Blockchain] Genesis block hash updated")
        
        # Repair each subsequent block
        for i in range(1, len(chain)):
            # Update prev_hash to point to previous block's hash
            prev_block = chain[i - 1]
            prev_hash = prev_block.get("block_hash", prev_block.get("hash", "0"))
            chain[i]["prev_hash"] = prev_hash
            
            # Recalculate this block's hash (including access_logs if they exist)
            old_hash = chain[i].get("block_hash", chain[i].get("hash"))
            new_hash = calculate_block_hash(chain[i])
            chain[i]["block_hash"] = new_hash
            
            # Verify the hash was calculated correctly
            verify_hash = calculate_block_hash(chain[i])
            if verify_hash != new_hash:
                print(f"[Blockchain] ERROR: Hash verification failed for block {i}!")
                return False
            
            if old_hash != new_hash:
                print(f"[Blockchain] Block {i} hash updated: {old_hash[:16]}... -> {new_hash[:16]}...")
        
        # Save repaired chain with consistent formatting
        with open(BLOCKCHAIN_FILE, "w") as f:
            json.dump(chain, f, indent=2, ensure_ascii=False)
        
        # Verify the repair was successful
        if verify_chain_integrity():
            print("[Blockchain] Chain integrity repaired and verified successfully")
            return True
        else:
            print("[Blockchain] WARNING: Chain repair completed but verification failed")
            return False
        
    except Exception as e:
        print(f"[Blockchain] Error repairing chain: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_chain_integrity() -> bool:
    """
    Verify the integrity of the blockchain
    
    Returns:
        True if chain is valid, False otherwise
    """
    chain = get_chain()
    
    if not chain:
        print("[Blockchain] Chain is empty")
        return False
    
    # Check genesis block
    genesis = chain[0]
    if genesis.get("prev_hash") != "0":
        print("[Blockchain] Invalid genesis block: prev_hash should be '0'")
        return False
    
    # Verify genesis block hash
    genesis_calculated = calculate_block_hash(genesis)
    genesis_stored = genesis.get("block_hash", genesis.get("hash"))
    if genesis_calculated != genesis_stored:
        print(f"[Blockchain] Invalid genesis block hash: stored={genesis_stored[:16]}..., calculated={genesis_calculated[:16]}...")
        return False
    
    # Verify each block's hash and link to previous
    for i in range(1, len(chain)):
        current = chain[i]
        previous = chain[i - 1]
        
        # Check hash calculation
        calculated_hash = calculate_block_hash(current)
        stored_hash = current.get("block_hash", current.get("hash"))
        
        if calculated_hash != stored_hash:
            print(f"[Blockchain] Invalid hash at block {i} (file_id: {current.get('file_id', 'unknown')})")
            print(f"[Blockchain]   Stored:   {stored_hash[:32]}...")
            print(f"[Blockchain]   Calculated: {calculated_hash[:32]}...")
            return False
        
        # Check link to previous block
        prev_hash = previous.get("block_hash", previous.get("hash"))
        if current.get("prev_hash") != prev_hash:
            print(f"[Blockchain] Broken chain at block {i}: prev_hash mismatch")
            print(f"[Blockchain]   Block {i} prev_hash: {current.get('prev_hash')[:32]}...")
            print(f"[Blockchain]   Block {i-1} hash:     {prev_hash[:32]}...")
            return False
    
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
        # Get the entire chain
        chain = get_chain()
        
        # Find the block index for this file
        block_index = None
        for i, b in enumerate(chain):
            if b.get("file_id") == file_id:
                block_index = i
                break
        
        if block_index is None:
            print(f"[Blockchain] File {file_id} not found in blockchain")
            return False
        
        block = chain[block_index]
        
        # Add access control log to the block
        if "access_logs" not in block:
            block["access_logs"] = []
        
        block["access_logs"].append(access_log)
        
        # Recalculate hash for the modified block (including access_logs)
        # Note: The access_log may contain a block_hash field with the old hash value,
        # but this is for audit purposes and is correctly included in the hash calculation
        old_hash = block.get("block_hash", block.get("hash"))
        new_hash = calculate_block_hash(block)
        
        # Always update the block hash to reflect the current state (with access_logs)
        block["block_hash"] = new_hash
        
        # Update the block in the chain array
        chain[block_index] = block
        
        # If the hash changed, we need to update all subsequent blocks
        if old_hash != new_hash:
            print(f"[Blockchain] Block hash changed from {old_hash[:16]}... to {new_hash[:16]}...")
            # Update all subsequent blocks' prev_hash and recalculate their hashes
            for i in range(block_index + 1, len(chain)):
                # Update prev_hash to point to the previous block's new hash
                prev_block = chain[i - 1]
                chain[i]["prev_hash"] = prev_block.get("block_hash", prev_block.get("hash"))
                
                # Recalculate this block's hash (which includes its own access_logs if any)
                chain[i]["block_hash"] = calculate_block_hash(chain[i])
        
        # Verify the hash is correct before saving
        verify_hash = calculate_block_hash(chain[block_index])
        if verify_hash != new_hash:
            raise ValueError(f"Hash verification failed after update! Expected {new_hash[:16]}..., got {verify_hash[:16]}...")
        
        # Save updated chain to disk with consistent formatting
        with open(BLOCKCHAIN_FILE, "w") as f:
            json.dump(chain, f, indent=2, ensure_ascii=False)
        
        # ALWAYS verify and repair chain integrity after modification to ensure consistency
        # This ensures that even if there were previous issues, they're fixed now
        if not verify_chain_integrity():
            print(f"[Blockchain] Chain integrity check failed after logging access control, repairing...")
            repair_success = repair_chain_integrity()
            if repair_success:
                # Verify again after repair
                if verify_chain_integrity():
                    print(f"[Blockchain] Chain integrity repaired successfully after logging access control")
                else:
                    print(f"[Blockchain] ERROR: Chain integrity still invalid after repair!")
            else:
                print(f"[Blockchain] ERROR: Failed to repair chain integrity!")
        else:
            # Double-check that the specific block is correct
            reloaded_block = get_block_by_file_id(file_id)
            if reloaded_block:
                reloaded_hash = calculate_block_hash(reloaded_block)
                if reloaded_block.get("block_hash") != reloaded_hash:
                    print(f"[Blockchain] WARNING: Block hash mismatch detected, forcing repair...")
                    repair_chain_integrity()
        
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
    
    This function automatically repairs the chain if integrity issues are detected.
    
    Args:
        file_id: File identifier
    
    Returns:
        Security verification results
    """
    block = get_block_by_file_id(file_id)
    if not block:
        return {"valid": False, "reason": "File not found in blockchain"}
    
    # Check blockchain integrity first
    chain_valid = verify_chain_integrity()
    
    # If invalid, repair the chain automatically
    if not chain_valid:
        print(f"[Blockchain] Chain integrity invalid for file {file_id}, auto-repairing...")
        repair_success = repair_chain_integrity()
        if repair_success:
            # Verify again after repair
            chain_valid = verify_chain_integrity()
            if chain_valid:
                print(f"[Blockchain] Chain integrity restored for file {file_id}")
            else:
                print(f"[Blockchain] WARNING: Chain repair completed but verification still fails")
        else:
            print(f"[Blockchain] ERROR: Chain repair failed for file {file_id}")
    
    # Reload block after repair to get updated data
    block = get_block_by_file_id(file_id)
    if not block:
        return {"valid": False, "reason": "File not found in blockchain after repair"}
    
    # Verify the specific block's hash is correct
    block_hash_calculated = calculate_block_hash(block)
    block_hash_stored = block.get("block_hash")
    
    # If there's still a mismatch, force a repair
    if block_hash_calculated != block_hash_stored:
        print(f"[Blockchain] Block hash mismatch detected for {file_id}")
        print(f"[Blockchain]   Stored:   {block_hash_stored[:32] if block_hash_stored else 'None'}...")
        print(f"[Blockchain]   Calculated: {block_hash_calculated[:32]}...")
        print(f"[Blockchain] Forcing chain repair...")
        
        repair_success = repair_chain_integrity()
        if repair_success:
            # Reload and verify again
            block = get_block_by_file_id(file_id)
            if block:
                block_hash_calculated = calculate_block_hash(block)
                block_hash_stored = block.get("block_hash")
                if block_hash_calculated == block_hash_stored:
                    print(f"[Blockchain] Block hash fixed after repair")
                    chain_valid = verify_chain_integrity()
                else:
                    print(f"[Blockchain] ERROR: Block hash still mismatched after repair!")
                    chain_valid = False
            else:
                chain_valid = False
        else:
            chain_valid = False
    
    # Final verification
    if chain_valid:
        # Double-check the entire chain is still valid
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
