# CHC Secure File Management System - Complete Working Flow Documentation

## 📋 Table of Contents
1. [System Overview](#system-overview)
2. [Complete Working Flow](#complete-working-flow)
3. [Data Storage Architecture](#data-storage-architecture)
4. [Blockchain Implementation](#blockchain-implementation)
5. [Firebase/Firestore Storage](#firebasefirestore-storage)
6. [Encryption Process (CHC Algorithm)](#encryption-process-chc-algorithm)
7. [Decryption Process](#decryption-process)
8. [Access Control Mechanism](#access-control-mechanism)
9. [Security Features](#security-features)

---

## 🎯 System Overview

The CHC (Contextual Hash Chain) Secure File Management System is a blockchain-linked secure cloud storage system that provides:

- **Contextual Encryption**: Each file encrypted with a unique seed derived from blockchain context
- **Forward Security**: CHC algorithm ensures cryptographic security through state chaining
- **Access Control**: Cryptographically enforced permissions via key wrapping
- **Immutable Audit Trail**: All operations logged to blockchain
- **Cloud Storage**: Encrypted files stored in Firebase Firestore

### System Architecture

```
┌─────────────────┐         ┌──────────────────┐         ┌─────────────────┐
│  React Frontend │  ←──→   │  Flask Backend    │  ←──→   │  Firebase       │
│  (Port 5173)    │  HTTP   │  (Port 5000)      │  API    │  Firestore      │
└─────────────────┘         └──────────────────┘         └─────────────────┘
                                      │
                                      │
                                      ↓
                            ┌──────────────────┐
                            │  Blockchain      │
                            │  (blockchain.json)│
                            └──────────────────┘
```

---

## 🔄 Complete Working Flow

### **Process 1: File Upload and Encryption Flow**

This is the complete 10-step process when a user uploads a file:

#### **Step 1: User Uploads File**
- **Location**: React Frontend (`CHCAPP/src/pages/Upload.tsx`)
- **Action**: User selects file via drag-and-drop or file picker
- **Validation**: 
  - File size check (max 16MB)
  - File format validation
  - User authentication check
- **Data Sent**: 
  - File binary data (multipart/form-data)
  - Authorized users list (comma-separated usernames)
  - Session token (Bearer token in Authorization header)

#### **Step 2: Backend Receives Upload Request**
- **Location**: Flask Backend (`app.py` - `/api/upload` endpoint)
- **Action**: 
  - Validates session token
  - Extracts file and metadata
  - Gets authenticated user as owner
- **Data Processed**:
  - Original filename
  - File content (bytes)
  - Owner username
  - Authorized users list

#### **Step 3: Generate File ID**
- **Location**: `encryption.py` - `generate_file_id()`
- **Method**: 
  ```python
  timestamp = time.time()
  data = f"{filename}:{owner}:{timestamp}".encode()
  hash_val = hashlib.sha256(data).hexdigest()
  file_id = f"file_{hash_val[:12]}"
  ```
- **Result**: Unique file identifier (e.g., `file_a1b2c3d4e5f6`)
- **Storage**: Used throughout system for file identification

#### **Step 4: Create Blockchain Block**
- **Location**: `blockchain.py` - `add_block()`
- **Process**:
  1. Create block structure:
     ```json
     {
       "index": chain_length,
       "timestamp": current_unix_timestamp,
       "file_id": "file_xxxxx",
       "owner": "username",
       "authorized_users": ["user1", "user2"],
       "prev_hash": previous_block_hash,
       "metadata": {
         "original_filename": "document.pdf",
         "size": 1024000,
         "upload_time": timestamp,
         "file_hash": "sha256_of_original_file"
       }
     }
     ```
  2. Calculate block hash:
     ```python
     block_hash = SHA256(block_data_without_hash)
     ```
  3. Append to blockchain
  4. Save to `blockchain.json`
- **Storage Location**: `blockchain.json` (local file)
- **Data Stored**: 
  - File metadata
  - Owner information
  - Authorized users
  - Block hash (SHA-256)
  - Previous block hash (chain linking)

#### **Step 5: Derive Encryption Seed**
- **Location**: `encryption.py` - `derive_seed()`
- **Process**:
  1. Get owner's master secret:
     ```python
     owner_secret = get_or_create_owner_secret(owner_name)
     # Returns 32-byte random secret (stored in memory)
     ```
  2. Create context string:
     ```python
     context = block_hash.encode() + str(timestamp).encode() + file_id.encode()
     ```
  3. Derive seed using HMAC-SHA256:
     ```python
     seed = hmac_sha256(owner_secret, context)
     # Returns 32-byte seed
     ```
- **Why This Works**:
  - **Unique per file**: Each file gets unique seed from blockchain context
  - **Tamper-proof**: Block hash ensures seed cannot be regenerated if blockchain is modified
  - **Owner-controlled**: Only owner can derive seed (has owner_secret)
- **Storage**: Seed is NOT stored directly - only wrapped versions stored

#### **Step 6: Encrypt File with CHC Algorithm**
- **Location**: `encryption.py` - `encrypt_chc()`
- **CHC Algorithm Details**:
  ```python
  state = seed  # Initial state is the derived seed
  ciphertext = b""
  BLOCK_SIZE = 32  # bytes per block
  
  for i in range(blocks):
      # Get current plaintext block
      p_block = plaintext[i*BLOCK_SIZE:(i+1)*BLOCK_SIZE]
      
      # Generate keystream for this block
      keystream = HMAC-SHA256(state, i.to_bytes(4, "big"))
      
      # Encrypt block (XOR with keystream)
      c_block = XOR(p_block, keystream[:len(p_block)])
      ciphertext += c_block
      
      # Update state with ciphertext (forward security)
      state = HMAC-SHA256(state, c_block)
  ```
- **Properties**:
  - **Forward Security**: Each block's encryption depends on previous ciphertext
  - **State Chaining**: State evolves with each encrypted block
  - **Cryptographic Security**: Uses HMAC-SHA256 for all operations
- **Result**: Encrypted file (same size as original, stream cipher)

#### **Step 7: Store Encrypted File in Firestore**
- **Location**: `data_manager.py` - `store_encrypted_file()`
- **Process**:
  1. Encode encrypted data as base64:
     ```python
     encrypted_data_b64 = base64.b64encode(encrypted_content).decode()
     ```
  2. Calculate checksum:
     ```python
     checksum = hashlib.sha256(encrypted_content).hexdigest()
     ```
  3. Create metadata document:
     ```json
     {
       "file_id": "file_xxxxx",
       "original_name": "document.pdf",
       "encrypted_data": "base64_encoded_encrypted_file...",
       "size_encrypted": 1024000,
       "storage_time": timestamp,
       "checksum": "sha256_hash",
       "block_hash": "blockchain_hash",
       "owner": "username",
       "authorized_users": ["user1", "user2"],
       "storage_type": "firestore_encrypted",
       "encryption_method": "CHC"
     }
     ```
  4. Store in Firestore collection: `metadata`
  5. Document ID: `file_id`
- **Storage Location**: Firebase Firestore
- **Collection**: `metadata`
- **Data Stored**:
  - Encrypted file (base64 encoded)
  - File metadata
  - Checksum for integrity verification
  - Blockchain reference (block_hash)

#### **Step 8: Wrap Seeds for Authorized Users**
- **Location**: `encryption.py` - `wrap_seed_for_user()`
- **Process**:
  For each authorized user (including owner):
  1. Generate user key:
     ```python
     user_key = SHA256(f"{username}:{file_id}".encode())
     ```
  2. Wrap seed:
     ```python
     wrapped_seed = XOR(seed, user_key)
     ```
  3. Encrypt wrapped seed with master key:
     ```python
     encrypted_wrapped = Fernet(master_key).encrypt(wrapped_seed)
     encrypted_wrapped_b64 = base64.b64encode(encrypted_wrapped).decode()
     ```
  4. Store in Firestore:
     - Collection: `key_vault`
     - Document ID: `{file_id}_{username}`
     - Data:
       ```json
       {
         "file_id": "file_xxxxx",
         "user": "username",
         "encrypted_seed": "base64_encrypted_wrapped_seed",
         "created_at": timestamp,
         "updated_at": timestamp
       }
       ```
- **Storage Location**: Firebase Firestore
- **Collection**: `key_vault`
- **Purpose**: Each authorized user gets their own wrapped seed to decrypt the file

#### **Step 9: Log Access Control to Blockchain**
- **Location**: `blockchain.py` - `log_access_control()`
- **Process**:
  1. Find block for file_id
  2. Add access log entry:
     ```json
     {
       "file_id": "file_xxxxx",
       "owner": "username",
       "authorized_users": ["user1", "user2"],
       "access_granted_at": timestamp,
       "encryption_method": "CHC",
       "block_hash": "block_hash_value"
     }
     ```
  3. Recalculate block hash (includes access_logs)
  4. Update all subsequent blocks' prev_hash (chain repair)
  5. Save updated blockchain
- **Storage Location**: `blockchain.json`
- **Purpose**: Immutable audit trail of access control setup

#### **Step 10: Complete Upload**
- **Result**: 
  - ✅ File encrypted and stored in Firestore
  - ✅ Blockchain record created
  - ✅ Wrapped seeds stored for authorized users
  - ✅ Access control logged
- **Response**: Returns file_id, block_hash, authorized_users to frontend

---

### **Process 2: File Decryption and Access Flow**

This is the complete 7-step process when a user requests to decrypt a file:

#### **Step 1: User Requests Decryption**
- **Location**: React Frontend (`CHCAPP/src/pages/Decrypt.tsx`)
- **Action**: User clicks "Decrypt" button on a file
- **Data Sent**:
  - File ID (from URL parameter)
  - Session token (Bearer token in Authorization header)

#### **Step 2: Retrieve Metadata from Blockchain**
- **Location**: `blockchain.py` - `get_block_by_file_id()`
- **Process**:
  1. Load blockchain from `blockchain.json`
  2. Search for block with matching file_id
  3. Return block data:
     ```json
     {
       "index": 1,
       "timestamp": 1234567890.123,
       "file_id": "file_xxxxx",
       "owner": "username",
       "authorized_users": ["user1", "user2"],
       "block_hash": "hash_value",
       "prev_hash": "previous_hash",
       "metadata": {...},
       "access_logs": [...]
     }
     ```
- **Storage Location**: `blockchain.json`
- **Purpose**: Get file metadata and access control information

#### **Step 3: Retrieve Encrypted File from Firestore**
- **Location**: `data_manager.py` - `retrieve_encrypted_file()`
- **Process**:
  1. Query Firestore:
     - Collection: `metadata`
     - Document ID: `file_id`
  2. Extract encrypted data:
     ```python
     encrypted_data_b64 = document.get('encrypted_data')
     encrypted_data = base64.b64decode(encrypted_data_b64)
     ```
  3. Verify checksum:
     ```python
     stored_checksum = document.get('checksum')
     current_checksum = SHA256(encrypted_data).hexdigest()
     assert current_checksum == stored_checksum
     ```
- **Storage Location**: Firebase Firestore - `metadata` collection
- **Data Retrieved**: Encrypted file content (base64 decoded)

#### **Step 4: Check Authorization**
- **Location**: `app.py` - `/api/decrypt/<file_id>` endpoint
- **Process**:
  1. Get current user from session token
  2. Check authorization:
     ```python
     is_authorized = (
         user_name == block['owner'] or 
         user_name in block['authorized_users']
     )
     ```
  3. If NOT authorized:
     - Log unauthorized attempt to blockchain
     - Return 403 Forbidden
  4. If authorized:
     - Continue to decryption
- **Purpose**: Ensure only authorized users can decrypt

#### **Step 5: Retrieve and Unwrap Seed**
- **Location**: `data_manager.py` - `retrieve_wrapped_seed()` + `encryption.py` - `unwrap_seed_for_user()`
- **Process**:
  1. Retrieve wrapped seed from Firestore:
     - Collection: `key_vault`
     - Document ID: `{file_id}_{username}`
     - Extract: `encrypted_seed` (base64)
  2. Decrypt with master key:
     ```python
     encrypted_wrapped = base64.b64decode(encrypted_seed_b64)
     wrapped_seed = Fernet(master_key).decrypt(encrypted_wrapped)
     ```
  3. Generate user key:
     ```python
     user_key = SHA256(f"{username}:{file_id}".encode())
     ```
  4. Unwrap seed:
     ```python
     seed = XOR(wrapped_seed, user_key)
     ```
- **Storage Location**: Firebase Firestore - `key_vault` collection
- **Result**: Original encryption seed (32 bytes)

#### **Step 6: Decrypt File with CHC Algorithm**
- **Location**: `encryption.py` - `decrypt_chc()`
- **CHC Decryption Algorithm**:
  ```python
  state = seed  # Same initial state as encryption
  plaintext = b""
  BLOCK_SIZE = 32
  
  for i in range(blocks):
      # Get current ciphertext block
      c_block = ciphertext[i*BLOCK_SIZE:(i+1)*BLOCK_SIZE]
      
      # Generate keystream (same as encryption)
      keystream = HMAC-SHA256(state, i.to_bytes(4, "big"))
      
      # Decrypt block (XOR with keystream)
      p_block = XOR(c_block, keystream[:len(c_block)])
      plaintext += p_block
      
      # Update state with ciphertext (same as encryption)
      state = HMAC-SHA256(state, c_block)
  ```
- **Why It Works**:
  - XOR is symmetric: `(A XOR B) XOR B = A`
  - State evolution is identical to encryption
  - Keystream generation is deterministic
- **Result**: Decrypted original file content

#### **Step 7: Log Success and Return File**
- **Location**: `blockchain.py` - `log_access_control()`
- **Process**:
  1. Log successful access:
     ```json
     {
       "file_id": "file_xxxxx",
       "user": "username",
       "access_time": timestamp,
       "access_granted": true,
       "decryption_successful": true
     }
     ```
  2. Update blockchain (recalculate hashes)
  3. Return decrypted file to user
- **Storage Location**: `blockchain.json` (access_logs array in block)
- **Response**: File download (binary data)

---

## 💾 Data Storage Architecture

### **Storage Locations Overview**

```
Project Root/
├── blockchain.json          # Blockchain ledger (local file)
├── users.json              # User accounts (local file)
├── sessions.json            # Active sessions (local file)
│
├── Firebase Firestore/
│   ├── metadata/           # Encrypted files + metadata
│   ├── key_vault/          # Wrapped seeds for users
│   ├── master_keys/        # System master keys
│   └── backups/            # System backups
│
└── secure_storage/         # Local fallback (if Firestore unavailable)
    ├── encrypted_files/
    ├── key_vault/
    └── metadata/
```

### **1. Local File Storage**

#### **blockchain.json**
- **Location**: Project root directory
- **Format**: JSON array of blocks
- **Structure**:
  ```json
  [
    {
      "index": 0,
      "timestamp": 1234567890.123,
      "file_id": "genesis",
      "owner": "system",
      "authorized_users": [],
      "prev_hash": "0",
      "data": "Genesis Block - CHC Secure Cloud Storage",
      "block_hash": "genesis_hash_value"
    },
    {
      "index": 1,
      "timestamp": 1234567891.456,
      "file_id": "file_a1b2c3d4e5f6",
      "owner": "alice",
      "authorized_users": ["bob", "charlie"],
      "prev_hash": "previous_block_hash",
      "block_hash": "current_block_hash",
      "metadata": {
        "original_filename": "document.pdf",
        "size": 1024000,
        "upload_time": 1234567891.456,
        "file_hash": "sha256_of_original_file"
      },
      "access_logs": [
        {
          "file_id": "file_a1b2c3d4e5f6",
          "owner": "alice",
          "authorized_users": ["bob", "charlie"],
          "access_granted_at": 1234567891.456,
          "encryption_method": "CHC",
          "block_hash": "current_block_hash"
        },
        {
          "file_id": "file_a1b2c3d4e5f6",
          "user": "bob",
          "access_time": 1234568000.789,
          "access_granted": true,
          "decryption_successful": true
        }
      ]
    }
  ]
  ```
- **Data Stored**:
  - File metadata (filename, size, owner)
  - Access control (owner, authorized users)
  - Block hashes (SHA-256)
  - Access logs (all access attempts)
  - Timestamps
- **Purpose**: Immutable audit trail, encryption context generation

#### **users.json**
- **Location**: Project root directory
- **Format**: JSON object
- **Structure**:
  ```json
  {
    "alice": {
      "username": "alice",
      "password_hash": "pbkdf2_sha256_hash",
      "salt": "random_salt_hex",
      "email": "alice@example.com",
      "role": "user",
      "created_at": 1234567890.123,
      "public_key": "hex_string",
      "private_key_encrypted": "hex_string",
      "files_uploaded": ["file_a1b2c3d4e5f6"],
      "files_accessible": ["file_x1y2z3w4v5u6"]
    }
  }
  ```
- **Data Stored**:
  - User credentials (hashed passwords)
  - User profile (email, role)
  - Cryptographic keys (simulated)
  - File references
- **Purpose**: User authentication and management

#### **sessions.json**
- **Location**: Project root directory
- **Format**: JSON object
- **Structure**:
  ```json
  {
    "session_token_hex_string": {
      "username": "alice",
      "role": "user",
      "login_time": 1234567890.123,
      "last_activity": 1234568000.789
    }
  }
  ```
- **Data Stored**:
  - Session tokens (64-char hex strings)
  - User information
  - Session timestamps
- **Purpose**: Active session management

### **2. Firebase Firestore Storage**

Firestore is organized into collections. Each collection contains documents.

#### **Collection: `metadata`**
- **Purpose**: Store encrypted files and file metadata
- **Document ID**: `file_id` (e.g., `file_a1b2c3d4e5f6`)
- **Document Structure**:
  ```json
  {
    "file_id": "file_a1b2c3d4e5f6",
    "original_name": "document.pdf",
    "encrypted_data": "base64_encoded_encrypted_file_content...",
    "size_encrypted": 1024000,
    "storage_time": 1234567891.456,
    "checksum": "sha256_hash_of_encrypted_data",
    "block_hash": "blockchain_block_hash",
    "owner": "alice",
    "authorized_users": ["bob", "charlie"],
    "storage_type": "firestore_encrypted",
    "encryption_method": "CHC"
  }
  ```
- **Data Stored**:
  - **Encrypted file content** (base64 encoded, can be up to 1MB per document)
  - File metadata (name, size, timestamps)
  - Integrity checksum
  - Blockchain reference
  - Access control information
- **Size Limit**: 1MB per document (Firestore limit)
- **Note**: For files > 700KB, consider using Firebase Cloud Storage instead

#### **Collection: `key_vault`**
- **Purpose**: Store wrapped encryption seeds for authorized users
- **Document ID**: `{file_id}_{username}` (e.g., `file_a1b2c3d4e5f6_alice`)
- **Document Structure**:
  ```json
  {
    "file_id": "file_a1b2c3d4e5f6",
    "user": "alice",
    "encrypted_seed": "base64_encrypted_wrapped_seed",
    "created_at": 1234567891.456,
    "updated_at": 1234567891.456
  }
  ```
- **Data Stored**:
  - Wrapped seed (encrypted with master key, then base64 encoded)
  - User reference
  - File reference
  - Timestamps
- **Purpose**: Per-user key management for access control
- **Security**: Double encryption (wrapped with user key, then encrypted with master key)

#### **Collection: `master_keys`**
- **Purpose**: Store system master encryption keys
- **Document ID**: `master_key` or `user_master_key`
- **Document Structure**:
  ```json
  {
    "key": "base64_encoded_fernet_key",
    "created_at": 1234567890.123,
    "updated_at": 1234567890.123
  }
  ```
- **Data Stored**:
  - Master encryption key (Fernet key, base64 encoded)
  - Creation/update timestamps
- **Purpose**: Encrypt wrapped seeds in key_vault
- **Security**: Critical - must be protected

#### **Collection: `backups`**
- **Purpose**: System backup storage
- **Document ID**: `backup_YYYYMMDD_HHMMSS`
- **Document Structure**:
  ```json
  {
    "backup_name": "backup_20240101_120000",
    "backup_time": 1234567890.123,
    "files": [...],
    "seeds": [...],
    "metadata_count": 10
  }
  ```
- **Data Stored**:
  - Backup metadata
  - File references (metadata only, not encrypted data)
  - Seed references
- **Purpose**: System recovery and backup

### **3. Data Flow Summary**

```
Upload Flow:
User File → Flask Backend → Encrypt (CHC) → Firestore (metadata collection)
                ↓
         Blockchain (blockchain.json)
                ↓
         Firestore (key_vault collection) - wrapped seeds

Decrypt Flow:
Firestore (metadata) → Encrypted File
Firestore (key_vault) → Wrapped Seed → Unwrap → Seed
Blockchain (blockchain.json) → Metadata & Access Control
                ↓
         Decrypt (CHC) → Original File
```

---

## ⛓️ Blockchain Implementation

### **How Blockchain Works in This System**

The blockchain serves multiple critical purposes:

1. **Encryption Context Generation**: Provides unique context (block hash, timestamp) for seed derivation
2. **Immutable Audit Trail**: Records all file operations and access attempts
3. **Access Control Logging**: Tracks who can access files and when
4. **Integrity Verification**: Hash chain ensures data hasn't been tampered with

### **Blockchain Structure**

#### **Block Format**
```json
{
  "index": 1,                    // Block number (0 = genesis)
  "timestamp": 1234567891.456,   // Unix timestamp
  "file_id": "file_xxxxx",       // Unique file identifier
  "owner": "username",           // File owner
  "authorized_users": ["user1"], // Users who can decrypt
  "prev_hash": "previous_hash",  // Hash of previous block
  "block_hash": "current_hash",  // SHA-256 hash of this block
  "metadata": {...},             // File metadata
  "access_logs": [...]          // Access control events
}
```

### **Block Hash Calculation**

```python
def calculate_block_hash(block_data):
    # Remove hash fields to avoid circular reference
    data = {k: v for k, v in block_data.items() 
            if k not in ('hash', 'block_hash')}
    
    # Convert to JSON with consistent formatting
    json_str = json.dumps(data, sort_keys=True, 
                         separators=(',', ':'), 
                         ensure_ascii=False)
    
    # Calculate SHA-256 hash
    return hashlib.sha256(json_str.encode('utf-8')).hexdigest()
```

**Properties**:
- **Deterministic**: Same data always produces same hash
- **Cryptographic**: SHA-256 ensures security
- **Includes all data**: Metadata, access_logs, everything

### **Chain Linking**

Each block (except genesis) links to previous block:

```python
block["prev_hash"] = previous_block["block_hash"]
```

**Why This Matters**:
- **Tamper Detection**: Changing any block breaks the chain
- **Immutability**: Previous blocks cannot be modified without breaking chain
- **Integrity**: Chain verification detects any modifications

### **Chain Integrity Verification**

```python
def verify_chain_integrity():
    # Check genesis block
    assert genesis["prev_hash"] == "0"
    assert genesis["block_hash"] == calculate_block_hash(genesis)
    
    # Check each subsequent block
    for i in range(1, len(chain)):
        current = chain[i]
        previous = chain[i-1]
        
        # Verify hash calculation
        assert current["block_hash"] == calculate_block_hash(current)
        
        # Verify chain link
        assert current["prev_hash"] == previous["block_hash"]
    
    return True
```

**Auto-Repair**: System automatically repairs chain if integrity check fails.

### **Access Control Logging**

When access control events occur, they're logged to the blockchain:

```python
# Upload event
access_log = {
    "file_id": "file_xxxxx",
    "owner": "alice",
    "authorized_users": ["bob"],
    "access_granted_at": timestamp,
    "encryption_method": "CHC",
    "block_hash": "block_hash"
}

# Successful access event
access_log = {
    "file_id": "file_xxxxx",
    "user": "bob",
    "access_time": timestamp,
    "access_granted": true,
    "decryption_successful": true
}

# Unauthorized attempt
access_log = {
    "file_id": "file_xxxxx",
    "unauthorized_user": "eve",
    "attempt_time": timestamp,
    "access_denied": true,
    "reason": "User not in authorized list"
}
```

**Important**: When access_logs are added, block hash is recalculated, and all subsequent blocks' prev_hash are updated.

### **Blockchain Storage**

- **File**: `blockchain.json`
- **Format**: JSON array
- **Location**: Project root directory
- **Persistence**: Saved to disk after every modification
- **Backup**: Included in system backups

### **Blockchain Use Cases**

1. **Seed Derivation Context**:
   ```python
   seed = HMAC-SHA256(owner_secret, block_hash + timestamp + file_id)
   ```
   - Block hash provides unique, immutable context
   - Ensures each file gets unique encryption seed

2. **Audit Trail**:
   - All file uploads recorded
   - All access attempts logged
   - Complete history of file operations

3. **Access Control Verification**:
   - Blockchain stores authorized users list
   - Immutable record of who can access files

4. **Security Verification**:
   - Chain integrity ensures data hasn't been tampered
   - Cryptographic verification of all operations

---

## ☁️ Firebase/Firestore Storage

### **Firebase Setup**

The system uses Firebase Firestore for cloud storage of encrypted files and keys.

#### **Initialization**
- **Location**: `data_manager.py` - `_init_firestore()`
- **Method**: Uses Firebase Admin SDK
- **Credentials**: Service account key file (JSON)
- **Environment Variable**: `GOOGLE_APPLICATION_CREDENTIALS`

### **Firestore Collections**

#### **1. Collection: `metadata`**

**Purpose**: Store encrypted files and metadata

**Document Structure**:
```json
{
  "file_id": "file_a1b2c3d4e5f6",
  "original_name": "document.pdf",
  "encrypted_data": "base64_encoded_string...",
  "size_encrypted": 1024000,
  "storage_time": 1234567891.456,
  "checksum": "sha256_hash",
  "block_hash": "blockchain_hash",
  "owner": "alice",
  "authorized_users": ["bob", "charlie"],
  "storage_type": "firestore_encrypted",
  "encryption_method": "CHC"
}
```

**Fields Explained**:
- `file_id`: Unique identifier (document ID)
- `original_name`: Original filename before encryption
- `encrypted_data`: **The actual encrypted file** (base64 encoded)
- `size_encrypted`: Size of encrypted file in bytes
- `storage_time`: When file was stored (Unix timestamp)
- `checksum`: SHA-256 hash of encrypted data (for integrity)
- `block_hash`: Reference to blockchain block
- `owner`: Username of file owner
- `authorized_users`: List of usernames who can decrypt
- `storage_type`: Always "firestore_encrypted"
- `encryption_method`: Always "CHC"

**Size Limits**:
- Firestore document limit: 1MB
- Base64 encoding adds ~33% overhead
- Effective limit: ~750KB original file size
- **Note**: For larger files, system warns but stores anyway (may fail for very large files)

**Operations**:
- **Store**: `store_encrypted_file()` - Creates/updates document
- **Retrieve**: `retrieve_encrypted_file()` - Gets encrypted data
- **Metadata**: `retrieve_file_metadata()` - Gets metadata without encrypted_data

#### **2. Collection: `key_vault`**

**Purpose**: Store wrapped encryption seeds for authorized users

**Document Structure**:
```json
{
  "file_id": "file_a1b2c3d4e5f6",
  "user": "alice",
  "encrypted_seed": "base64_encrypted_wrapped_seed",
  "created_at": 1234567891.456,
  "updated_at": 1234567891.456
}
```

**Fields Explained**:
- `file_id`: Reference to file
- `user`: Username (part of document ID)
- `encrypted_seed`: **Wrapped seed, encrypted with master key, base64 encoded**
- `created_at`: When seed was created
- `updated_at`: Last update time

**Document ID Format**: `{file_id}_{username}`

**Example**: `file_a1b2c3d4e5f6_alice`

**Security Layers**:
1. **Seed Wrapping**: `seed XOR user_key` (user-specific)
2. **Master Key Encryption**: Fernet encryption with master key
3. **Base64 Encoding**: For Firestore storage

**Operations**:
- **Store**: `store_wrapped_seed()` - Creates document for user
- **Retrieve**: `retrieve_wrapped_seed()` - Gets and decrypts seed

#### **3. Collection: `master_keys`**

**Purpose**: Store system master encryption keys

**Document Structure**:
```json
{
  "key": "base64_encoded_fernet_key",
  "created_at": 1234567890.123,
  "updated_at": 1234567890.123
}
```

**Document IDs**:
- `master_key`: For encrypting wrapped seeds in key_vault
- `user_master_key`: For user key management (if used)

**Security**: 
- **Critical**: Master keys must be protected
- **Generation**: Fernet.generate_key() (256-bit)
- **Storage**: Base64 encoded in Firestore

**Operations**:
- **Load/Create**: `load_or_create_master_key()` - Gets or creates master key

#### **4. Collection: `backups`**

**Purpose**: System backup storage

**Document Structure**:
```json
{
  "backup_name": "backup_20240101_120000",
  "backup_time": 1234567890.123,
  "files": [
    {
      "file_id": "file_xxxxx",
      "original_name": "document.pdf",
      // ... metadata (without encrypted_data)
    }
  ],
  "seeds": [
    {
      "file_id": "file_xxxxx",
      "user": "alice",
      // ... seed metadata
    }
  ],
  "metadata_count": 10
}
```

**Note**: Backups store metadata only, not full encrypted files (to save space).

### **Firestore Data Flow**

```
Upload:
1. Encrypt file → encrypted_data
2. Base64 encode → encrypted_data_b64
3. Store in metadata/{file_id}
4. Wrap seeds → encrypted_seed
5. Store in key_vault/{file_id}_{username}

Decrypt:
1. Get from metadata/{file_id} → encrypted_data_b64
2. Base64 decode → encrypted_data
3. Get from key_vault/{file_id}_{username} → encrypted_seed
4. Decrypt with master key → wrapped_seed
5. Unwrap with user key → seed
6. Decrypt file with seed → plaintext
```

### **Firestore Security**

- **Authentication**: Firebase Admin SDK (service account)
- **Authorization**: Server-side only (no client access)
- **Encryption**: 
  - Files encrypted with CHC before storage
  - Seeds encrypted with master key
- **Integrity**: Checksums verify data integrity

---

## 🔐 Encryption Process (CHC Algorithm)

### **Contextual Hash Chain (CHC) Encryption**

CHC is a stream cipher algorithm that provides forward security through state chaining.

### **Step-by-Step Encryption Process**

#### **1. Seed Derivation**

```python
# Get owner's master secret (32 bytes, stored in memory)
owner_secret = get_or_create_owner_secret(owner_name)

# Create context from blockchain
context = block_hash.encode() + str(timestamp).encode() + file_id.encode()

# Derive seed using HMAC-SHA256
seed = hmac_sha256(owner_secret, context)
# Returns 32-byte seed
```

**Key Properties**:
- **Unique**: Each file gets unique seed from blockchain context
- **Tamper-proof**: Block hash ensures immutability
- **Owner-controlled**: Only owner can derive seed

#### **2. CHC Encryption Algorithm**

```python
def encrypt_chc(plaintext: bytes, seed: bytes) -> bytes:
    state = seed  # Initial state is the derived seed
    ciphertext = b""
    BLOCK_SIZE = 32  # bytes per block
    blocks = math.ceil(len(plaintext) / BLOCK_SIZE)
    
    for i in range(blocks):
        # Get current plaintext block
        start = i * BLOCK_SIZE
        end = min((i + 1) * BLOCK_SIZE, len(plaintext))
        p_block = plaintext[start:end]
        
        # Generate keystream for this block
        keystream = hmac_sha256(state, i.to_bytes(4, "big"))
        
        # Encrypt block (XOR with keystream)
        c_block = xor_bytes(p_block, keystream[:len(p_block)])
        ciphertext += c_block
        
        # Update state with ciphertext (forward security)
        state = hmac_sha256(state, c_block)
    
    return ciphertext
```

**Algorithm Properties**:
- **Forward Security**: Each block's encryption depends on previous ciphertext
- **State Chaining**: State evolves with each encrypted block
- **Stream Cipher**: Same size as plaintext (no padding)
- **Cryptographic Security**: Uses HMAC-SHA256 for all operations

#### **3. Encryption Flow Diagram**

```
Plaintext File
    ↓
Divide into 32-byte blocks
    ↓
For each block:
    ├─ Generate keystream: HMAC(state, block_index)
    ├─ Encrypt: plaintext_block XOR keystream
    └─ Update state: HMAC(state, ciphertext_block)
    ↓
Ciphertext File (same size)
```

### **Why CHC is Secure**

1. **Forward Security**: 
   - If one block is compromised, previous blocks remain secure
   - State evolution prevents retrospective decryption

2. **Contextual Uniqueness**:
   - Each file gets unique seed from blockchain
   - Same file uploaded twice gets different encryption

3. **Cryptographic Strength**:
   - HMAC-SHA256 provides cryptographic security
   - 256-bit seed ensures strong encryption

4. **Tamper Detection**:
   - Seed derived from blockchain hash
   - Any blockchain modification changes seed
   - Decryption fails if blockchain is tampered

---

## 🔓 Decryption Process

### **Step-by-Step Decryption Process**

#### **1. Retrieve Components**

```python
# 1. Get encrypted file from Firestore
encrypted_data = retrieve_encrypted_file(file_id)

# 2. Get wrapped seed from Firestore
wrapped_seed = retrieve_wrapped_seed(file_id, username)

# 3. Get metadata from blockchain
block = get_block_by_file_id(file_id)
```

#### **2. Authorization Check**

```python
# Verify user is authorized
is_authorized = (
    user_name == block['owner'] or 
    user_name in block['authorized_users']
)

if not is_authorized:
    # Log unauthorized attempt
    log_access_control(file_id, {
        "unauthorized_user": user_name,
        "access_denied": True
    })
    return 403 Forbidden
```

#### **3. Unwrap Seed**

```python
# 1. Decrypt wrapped seed with master key
encrypted_wrapped = base64.b64decode(encrypted_seed_b64)
wrapped_seed = Fernet(master_key).decrypt(encrypted_wrapped)

# 2. Generate user key
user_key = SHA256(f"{username}:{file_id}".encode())

# 3. Unwrap seed
seed = XOR(wrapped_seed, user_key)
```

#### **4. CHC Decryption Algorithm**

```python
def decrypt_chc(ciphertext: bytes, seed: bytes) -> bytes:
    state = seed  # Same initial state as encryption
    plaintext = b""
    BLOCK_SIZE = 32
    blocks = math.ceil(len(ciphertext) / BLOCK_SIZE)
    
    for i in range(blocks):
        # Get current ciphertext block
        start = i * BLOCK_SIZE
        end = min((i + 1) * BLOCK_SIZE, len(ciphertext))
        c_block = ciphertext[start:end]
        
        # Generate keystream (same as encryption)
        keystream = hmac_sha256(state, i.to_bytes(4, "big"))
        
        # Decrypt block (XOR with keystream)
        p_block = xor_bytes(c_block, keystream[:len(c_block)])
        plaintext += p_block
        
        # Update state with ciphertext (same as encryption)
        state = hmac_sha256(state, c_block)
    
    return plaintext
```

**Why Decryption Works**:
- **XOR Symmetry**: `(A XOR B) XOR B = A`
- **Identical State Evolution**: State updates match encryption
- **Deterministic Keystream**: Same inputs produce same keystream

#### **5. Log Success**

```python
# Log successful decryption
log_access_control(file_id, {
    "file_id": file_id,
    "user": user_name,
    "access_time": time.time(),
    "access_granted": True,
    "decryption_successful": True
})
```

### **Decryption Flow Diagram**

```
Encrypted File (Firestore)
    ↓
Wrapped Seed (Firestore)
    ↓
Unwrap Seed:
    ├─ Decrypt with master key
    ├─ Generate user key
    └─ XOR unwrap
    ↓
Seed (32 bytes)
    ↓
CHC Decryption:
    ├─ For each block:
    │   ├─ Generate keystream: HMAC(state, block_index)
    │   ├─ Decrypt: ciphertext_block XOR keystream
    │   └─ Update state: HMAC(state, ciphertext_block)
    ↓
Plaintext File
```

---

## 🔒 Access Control Mechanism

### **How Access Control Works**

Access control is enforced through multiple layers:

#### **1. Blockchain-Based Authorization**

```python
# Check if user is authorized
block = get_block_by_file_id(file_id)
is_authorized = (
    user_name == block['owner'] or 
    user_name in block['authorized_users']
)
```

- **Owner**: Always authorized
- **Authorized Users**: List stored in blockchain
- **Immutable**: Cannot be modified without breaking chain

#### **2. Cryptographic Key Wrapping**

```python
# Each authorized user gets wrapped seed
for user in authorized_users + [owner]:
    user_key = SHA256(f"{user}:{file_id}".encode())
    wrapped_seed = XOR(seed, user_key)
    # Store wrapped seed in Firestore
```

- **User-Specific**: Each user has unique wrapped seed
- **Cryptographic**: Cannot unwrap without user key
- **Stored Securely**: Encrypted with master key in Firestore

#### **3. Unauthorized Access Prevention**

```python
if not is_authorized:
    # Log attempt
    log_access_control(file_id, {
        "unauthorized_user": user_name,
        "access_denied": True,
        "reason": "User not in authorized list"
    })
    return 403 Forbidden
```

- **Blocked**: Unauthorized users cannot decrypt
- **Logged**: All attempts recorded in blockchain
- **Audit Trail**: Complete history of access attempts

### **Access Control Flow**

```
User Requests Decryption
    ↓
Check Blockchain Authorization
    ├─ Owner? → Authorized
    ├─ In authorized_users? → Authorized
    └─ Neither? → Unauthorized (blocked)
    ↓
If Authorized:
    ├─ Retrieve wrapped seed from Firestore
    ├─ Unwrap with user key
    └─ Decrypt file
    ↓
If Unauthorized:
    ├─ Log attempt to blockchain
    └─ Return 403 Forbidden
```

---

## 🛡️ Security Features

### **1. Cryptographic Security**

- **HMAC-SHA256**: All cryptographic operations use HMAC-SHA256
- **256-bit Seeds**: Strong encryption keys
- **PBKDF2**: Password hashing with 100,000 iterations
- **Fernet Encryption**: Symmetric encryption for key vault

### **2. Forward Security**

- **CHC Algorithm**: State chaining prevents retrospective decryption
- **State Evolution**: Each block's encryption depends on previous
- **Tamper Detection**: Blockchain modification breaks decryption

### **3. Access Control**

- **Cryptographic Enforcement**: Key wrapping ensures only authorized users can decrypt
- **Blockchain-Based**: Immutable authorization list
- **Per-User Keys**: Each user has unique wrapped seed

### **4. Integrity Verification**

- **Checksums**: SHA-256 checksums verify file integrity
- **Blockchain Hash Chain**: Detects any tampering
- **Chain Verification**: Automatic integrity checks

### **5. Audit Trail**

- **Complete Logging**: All operations logged to blockchain
- **Immutable Records**: Cannot be modified after creation
- **Access History**: Complete history of file access

### **6. Cloud Storage Security**

- **Encrypted Storage**: Files encrypted before storage
- **Double Encryption**: Seeds encrypted with master key
- **Server-Side Only**: No client access to Firestore
- **Service Account**: Secure authentication

---

## 📊 Summary

### **Complete Data Flow**

```
UPLOAD:
User → Frontend → Backend → Generate File ID
                              ↓
                         Create Blockchain Block
                              ↓
                         Derive Seed (from blockchain context)
                              ↓
                         Encrypt File (CHC)
                              ↓
                         Store in Firestore (metadata)
                              ↓
                         Wrap Seeds for Users
                              ↓
                         Store in Firestore (key_vault)
                              ↓
                         Log to Blockchain

DECRYPT:
User → Frontend → Backend → Get Blockchain Metadata
                              ↓
                         Get Encrypted File (Firestore)
                              ↓
                         Check Authorization
           