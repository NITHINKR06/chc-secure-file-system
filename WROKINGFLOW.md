# CHC Secure File Management System — Working Flow Guide

This document explains the full working flow of the project, covering how each component interacts, what data is stored where, and how the blockchain, Firebase storage, and CHC encryption/decryption processes operate together.

---

## 1. System Overview

- **Frontend**: React + TypeScript application (`CHCAPP/`) served by Vite on `http://127.0.0.1:5173`.
- **Backend**: Flask API (`app.py`) running on `http://127.0.0.1:5000`.
- **Blockchain**: Custom SHA-256 linked ledger stored locally in `blockchain.json`.
- **Cloud Storage**: Firebase Firestore for encrypted files, metadata, wrapped seeds, and master keys.
- **Authentication**: JSON-based user and session stores (`users.json`, `sessions.json`) handled by `auth.py`.
- **Encryption**: Contextual Hash Chain (CHC) algorithm implemented in `encryption.py`.
- **Data Management**: `data_manager.py` orchestrates Firestore interaction and key vault storage.

```
┌──────────────┐    HTTPS    ┌───────────────┐    Firestore    ┌───────────────┐
│ React (Vite) │  ─────────► │ Flask (API)   │  ─────────────► │ Cloud Storage │
└──────────────┘             └───────────────┘                 └───────────────┘
         │                          │                                   │
         ▼                          ▼                                   ▼
  Local browser             Local blockchain                     Key vault + metadata
  storage (token)            `blockchain.json`                         (Firestore)
```

---

## 2. Complete Working Flow

### 2.1 Upload + Encryption (7 steps)

1. **User Uploads File**
   - Source: `CHCAPP/src/pages/Upload.tsx`
   - Checks session token, file size (≤16 MB), and collects optional comma-separated authorized users.
   - Sends `multipart/form-data` (`file`, `authorized_users`) and `Authorization: Bearer <token>` to `POST /api/upload`.

2. **API Validates Request**
   - Function: `api_upload()` in `app.py`
   - Verifies the session via `UserManager.verify_session` (token lookup in `sessions.json`).
   - Reads file bytes into memory, runs a size guard, and collects owner + authorized users.

3. **Generate File ID**
   - Function: `encryption.generate_file_id(filename, owner)`
   - Creates deterministic ID: `file_<first 12 chars of SHA256(filename + owner + timestamp)>`.

4. **Create Blockchain Block**
   - Function: `blockchain.add_block(file_id, owner, authorized_users, metadata)`
   - Builds a new block with metadata (`original_filename`, `size`, `upload_time`, `file_hash = SHA256(file_bytes)`).
   - Calculates `prev_hash` link and current `block_hash` using `calculate_block_hash`.
   - Persists chain to `blockchain.json`.

5. **Derive Encryption Seed (Contextual)**
   - Functions: `encryption.get_or_create_owner_secret(owner)` + `encryption.derive_seed(owner_secret, block_hash, timestamp, file_id)`
   - Owner secret: 32-byte random value (in-memory map per owner).
   - Seed: `seed = HMAC_SHA256(owner_secret, block_hash || timestamp || file_id)`.
   - Binding to blockchain context provides immutability and uniqueness.

6. **Encrypt with CHC Algorithm**
   - Function: `encryption.encrypt_chc(plaintext, seed)`
   - Iterates through 32-byte blocks:
     ```
     state = seed
     for block_index, plaintext_block in enumerate(plaintext):
         keystream = HMAC_SHA256(state, block_index)
         cipher_block = plaintext_block XOR keystream
         state = HMAC_SHA256(state, cipher_block)   # forward security
     ```
   - Produces ciphertext of equal length.

7. **Store Encrypted File & Seeds**
   - Encrypted file: `data_manager.store_encrypted_file(...)`
     - Base64 encodes ciphertext, computes checksum, and stores document under `metadata/<file_id>` in Firestore.
   - Wrapped seeds (for each authorized user + owner):
     - `encryption.generate_user_key(username, file_id)` → SHA256 of `username:file_id`.
     - `encryption.wrap_seed_for_user(seed, user_key)` → XOR, then encrypted with Fernet master key via `data_manager.store_wrapped_seed`.
     - Stored under `key_vault/<file_id>_<username>` in Firestore.
   - Access control log appended to blockchain via `blockchain.log_access_control`.

### 2.2 Decryption + Access (7 steps)

1. **User Initiates Decrypt**
   - Frontend: `CHCAPP/src/pages/Decrypt.tsx`
   - Calls `POST /api/decrypt/<file_id>` with `Authorization: Bearer <token>`.

2. **Validate Session & Fetch Metadata**
   - `api_decrypt(file_id)` verifies session token.
   - Loads metadata from in-memory cache or Firestore (`data_manager.retrieve_file_metadata`).
   - Retrieves blockchain block (`blockchain.get_block_by_file_id`).

3. **Authorization Check**
   - Confirms: `current_user == owner OR current_user in authorized_users`.
   - Unauthorized attempts logged with `access_denied` in blockchain; aborts with 403.

4. **Fetch Ciphertext & Wrapped Seed**
   - Ciphertext: `data_manager.retrieve_encrypted_file(file_id)` (base64 decoded and checksum verified).
   - Wrapped seed: `data_manager.retrieve_wrapped_seed(file_id, username)` (Fernet decrypt → XOR unwrap).
   - Regenerates user key with `encryption.generate_user_key`.

5. **Derive Decryption Seed**
   - `seed = encryption.unwrap_seed_for_user(wrapped_seed, user_key)` (XOR reversal).
   - Seed matches encryption seed because blockchain context is identical.

6. **Decrypt with CHC**
   - `encryption.decrypt_chc(ciphertext, seed)` mirrors encryption loop:
     ```
     state = seed
     for block_index, cipher_block in enumerate(ciphertext):
         keystream = HMAC_SHA256(state, block_index)
         plaintext_block = cipher_block XOR keystream
         state = HMAC_SHA256(state, cipher_block)
     ```
   - Returns original file bytes.

7. **Log Outcome & Respond**
   - Success log: `blockchain.log_access_control` with `access_granted` and `decryption_successful`.
   - Sends decrypted bytes back via `send_file` with original filename.

---

## 3. Data Storage Architecture

### 3.1 Local JSON Stores

| File              | Managed By | Purpose | Sample Fields |
|-------------------|------------|---------|---------------|
| `blockchain.json` | `blockchain.py` | Immutable ledger of file metadata, access logs, hashes | `index`, `file_id`, `owner`, `authorized_users`, `metadata`, `access_logs`, `prev_hash`, `block_hash` |
| `users.json`      | `auth.py`  | User accounts (PBKDF2 hashed passwords) | `username`, `password_hash`, `salt`, `role`, `files_uploaded`, `files_accessible` |
| `sessions.json`   | `auth.py`  | Active sessions keyed by token | `username`, `role`, `login_time`, `last_activity` |

### 3.2 Firebase Firestore Collections (Cloud)

| Collection      | Document ID                    | Contents |
|-----------------|--------------------------------|----------|
| `metadata`      | `<file_id>`                    | `encrypted_data` (base64), `size_encrypted`, `checksum`, `storage_time`, `owner`, `authorized_users`, `block_hash`, `encryption_method` |
| `key_vault`     | `<file_id>_<username>`         | `encrypted_seed` (wrapped seed encrypted with Fernet master key), `created_at`, `updated_at` |
| `master_keys`   | `master_key`, `user_master_key` | Base64-encoded Fernet keys + timestamps |
| `backups`       | `backup_<timestamp>`           | Metadata snapshots for recovery (no ciphertext) |

**Data flow**:
```
Upload:
   plaintext → encrypt_chc → ciphertext → Firestore metadata.encrypted_data
   seed → wrap for each user → encrypted_seed → Firestore key_vault

Decrypt:
   metadata.encrypted_data → ciphertext
   key_vault.encrypted_seed → wrapped seed → seed
   ciphertext + seed → decrypt_chc → plaintext
```

---

## 4. Blockchain Mechanics

- **Genesis block** created in `blockchain.init_chain()` when module loads.
- **Block creation**: `blockchain.add_block` (during upload) adds metadata and computes hash.
- **Access logging**: `blockchain.log_access_control` appends events (authorized access, unauthorized attempts, decryption failures).
- **Integrity checks**: `verify_chain_integrity` ensures each block hash matches computed hash and `prev_hash` links are valid.
- **Auto-repair**: `repair_chain_integrity` recalculates hashes and previous links if discrepancies are detected.
- **Usage in encryption**: `block_hash` and `timestamp` feed into CHC seed derivation, making the blockchain an intrinsic part of encryption context.

Example access log entry appended to a block:

```
{
  "file_id": "file_ab12cd34ef56",
  "user": "alice",
  "access_time": 1731425300.12,
  "access_granted": true,
  "decryption_successful": true
}
```

---

## 5. Firebase (Cloud) Storage Details

### 5.1 Encrypted Files (`metadata` collection)
- `encrypted_data`: base64-encoded ciphertext.
- `checksum`: SHA-256 of raw ciphertext to ensure integrity on retrieval.
- `owner`, `authorized_users`, and `block_hash` replicate blockchain metadata for quick API access.
- `size_encrypted` enables UI display and storage stats.

### 5.2 Wrapped Seeds (`key_vault` collection)
- `encrypted_seed`: Fernet-encrypted bytes of `(seed XOR user_key)`.
- Allows only intended user (with regenerated user key) to obtain original seed.
- Master key fetched via `DataManager.load_or_create_master_key` (stored in `master_keys` collection).

### 5.3 Master Keys (`master_keys` collection)
- `master_key`: used to encrypt wrapped seeds before storing in `key_vault`.
- Stored base64-encoded; generated once and reused.

### 5.4 Backups (`backups` collection)
- `DataManager.create_backup` aggregates metadata and seeds for recovery without storing encrypted file payloads.

---

## 6. CHC Encryption & Decryption

### 6.1 Key Components
- `BLOCK_SIZE = 32` bytes.
- HMAC-SHA256 used for keystream generation and state updates.
- XOR used for reversible encryption of each block.
- State chaining provides **forward security**: compromise of later blocks doesn’t reveal earlier blocks.

### 6.2 Seed Lifecycle
1. Owner secret (per user) generated once (`os.urandom(32)`).
2. Seed derived from blockchain context for each file.
3. Seed wrapped per user and stored securely.
4. Unwrapped on demand during decryption.

### 6.3 User Key Derivation
- `generate_user_key(username, file_id)` = SHA-256 hash of `<username>:<file_id>`.
- Ensures consistent symmetric key without storing plaintext keys.

---

## 7. How Data Moves (End-to-End)

### Upload Sequence
```
Browser ──(file, users, token)──► Flask API
    ├─ generate file_id
    ├─ add blockchain block
    ├─ derive seed from blockchain context
    ├─ encrypt file (CHC)
    ├─ store encrypted file in Firestore `metadata`
    └─ wrap seed per user → Firestore `key_vault`
```

### Decrypt Sequence
```
Browser ──(token)──► Flask API
    ├─ verify session + authorization
    ├─ fetch ciphertext from Firestore `metadata`
    ├─ fetch wrapped seed for user from `key_vault`
    ├─ unwrap seed (Fernet decrypt + XOR)
    ├─ decrypt ciphertext (CHC)
    └─ log access event on blockchain and return plaintext as file download
```

---

## 8. Additional Components

- **Authentication (`auth.py`)**
  - PBKDF2-SHA256 password hashing with per-user salt.
  - Session tokens (hex) stored in `sessions.json`.
  - Default admin created via environment variables or fallback credentials.

- **Data Manager (`data_manager.py`)**
  - Initializes Firebase Admin SDK using `GOOGLE_APPLICATION_CREDENTIALS`.
  - Provides integrity checks (`verify_file_integrity`) and cleanup/backups.

- **Developer Runner (`dev_runner.py`)**
  - Launches backend and frontend together (`python dev_runner.py`).

- **Frontend (`CHCAPP/`)**
  - `Files.tsx` shows files user owns or has access to, using `GET /api/files`.
  - `Blockchain.tsx` visualizes blockchain via `GET /api/blockchain`.
  - `SecurityAudit.tsx` uses `GET /api/security/<file_id>` for audit trail and integrity status.

---

## 9. Operational Notes

- **Setup**: Install Python dependencies (`pip install -r requirements.txt`), run `npm install` in `CHCAPP/`, configure `.env`, and set Firebase credentials.
- **Run**: `python dev_runner.py` (recommended) or run backend/frontend separately.
- **Limits**: Firestore document size (~1 MB) affects maximum encrypted payload per file; consider Firebase Cloud Storage for larger files.
- **Security Practices**: Change default admin password, ensure `.env` and Firebase credentials are secured, and maintain backups of `blockchain.json`.

---

## 10. Quick Reference to Key Functions

| Operation            | Function(s) | File |
|---------------------|-------------|------|
| Upload endpoint     | `api_upload` | `app.py` |
| Decrypt endpoint    | `api_decrypt` | `app.py` |
| Blockchain add/log  | `add_block`, `log_access_control` | `blockchain.py` |
| CHC encrypt/decrypt | `encrypt_chc`, `decrypt_chc` | `encryption.py` |
| Seed wrap/unwrap    | `wrap_seed_for_user`, `unwrap_seed_for_user` | `encryption.py` |
| Firestore store     | `store_encrypted_file`, `store_wrapped_seed` | `data_manager.py` |
| Firestore retrieve  | `retrieve_encrypted_file`, `retrieve_wrapped_seed` | `data_manager.py` |
| Session management  | `login_user`, `verify_session`, `logout_user` | `auth.py` |

---

With this document, you can trace every step of the system—from how data enters and leaves the application, to the precise storage locations and cryptographic safeguards that keep files secure. Use it as the authoritative reference for project flow, storage design, and security operations.

