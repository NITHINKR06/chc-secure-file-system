<div align="center">

# 🔐 CHC Secure File System

### Blockchain-Linked Contextual Encryption for Secure Cloud Storage

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=flat-square&logo=python)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.3.3-black?style=flat-square&logo=flask)](https://flask.palletsprojects.com)
[![React](https://img.shields.io/badge/React-TypeScript-61DAFB?style=flat-square&logo=react)](https://react.dev)
[![Tailwind](https://img.shields.io/badge/Tailwind-CSS-38B2AC?style=flat-square&logo=tailwind-css)](https://tailwindcss.com)
[![License](https://img.shields.io/badge/License-Educational-green?style=flat-square)](#license)

A secure file management system implementing **Contextual Hash Chain (CHC)** encryption with blockchain-backed access control, per-user key wrapping, and a full audit trail.

[Features](#-features) · [Architecture](#-architecture) · [Quick Start](#-quick-start) · [API Reference](#-api-reference) · [Security](#-security-model) · [Troubleshooting](#-troubleshooting)

</div>

---

## ✨ Features

| Category | What's included |
|---|---|
| 🔒 **Encryption** | CHC algorithm with forward security, HMAC-SHA256 state chaining |
| 🔑 **Key Management** | Per-user Fernet-wrapped seeds, PBKDF2-derived user keys, encrypted owner secrets |
| ⛓️ **Blockchain** | Immutable SHA-256 hash chain, tamper-proof audit trail |
| 👤 **Auth** | PBKDF2-SHA256 passwords, configurable session timeout, role-based access |
| 🗄️ **Storage** | Firebase Firestore off-chain storage with local fallback |
| 🖥️ **Frontend** | React + TypeScript + Vite + Tailwind CSS, fully responsive |

---

## 🏗️ Architecture

![System Architecture](static/flowchart.png)

The system is organized into three layers:

| Layer | Components | Responsibility |
|---|---|---|
| **Presentation** | `CHCAPP` (React) | File upload, decrypt requests, blockchain viewer |
| **Application Logic** | `app.py`, `auth.py`, `encryption.py`, `blockchain.py`, `data_manager.py` | Auth, CHC encryption, key wrapping, audit logging |
| **Data & Storage** | Firebase Firestore + local JSON files | Ciphertext, wrapped seeds, metadata, sessions |

### Upload Flow

```
User uploads file
      │
      ▼
Generate File ID ──► Create Blockchain Block
                              │
                              ▼
                   Get Block Hash + Timestamp
                              │
                              ▼
              Derive Seed = HMAC(owner_secret, hash‖ts‖id)
                              │
                              ▼
                   CHC Encrypt file (32-byte blocks)
                              │
                         ┌────┴────┐
                         ▼         ▼
               Store ciphertext  Wrap seed per user
               (Firestore)       (Fernet + PBKDF2 key)
                                       │
                                       ▼
                            Log access control → Blockchain ✓
```

### Decryption Flow

```
User requests file
      │
      ▼
Verify session token
      │
      ▼
Fetch metadata from blockchain
      │
      ▼
Check authorisation (owner or authorised user?)
      │ ✓
      ▼
Unwrap seed with user's Fernet key
      │
      ▼
CHC Decrypt → send plaintext file
      │
      ▼
Log successful access → Blockchain ✓
```

---

## 📁 Project Structure

```
chc-secure-file-system-main/
│
├── app.py                  # Flask API server (all endpoints)
├── auth.py                 # User auth, sessions, PBKDF2 passwords
├── encryption.py           # CHC algorithm, key derivation, Fernet wrapping
├── blockchain.py           # Local SHA-256 hash chain
├── data_manager.py         # Firestore / local storage abstraction
├── dev_runner.py           # Starts backend + frontend together
├── requirements.txt        # Python dependencies
├── render.yaml             # Render.com deployment config
├── Procfile                # Gunicorn entry point
│
├── CHCAPP/                 # React + TypeScript frontend
│   ├── src/
│   │   ├── pages/          # Upload, Files, Decrypt, Blockchain, etc.
│   │   ├── components/     # Shared UI components
│   │   └── utils/api.ts    # Axios API client
│   ├── public/
│   └── package.json
│
└── secure_storage/
    ├── encrypted_files/    # Stored ciphertext
    ├── key_vault/          # Wrapped seeds + master keys
    └── metadata/           # File metadata
```

---

## 🚀 Quick Start

### Prerequisites

- Python **3.8+**
- Node.js **16+**
- A Firebase project (for Firestore) — or use the local fallback

### 1 · Clone & install backend

```bash
git clone <repository-url>
cd chc-secure-file-system-main
pip install -r requirements.txt
```

### 2 · Configure environment

Create a `.env` file in the project root:

```env
# Required
SECRET_KEY=change_me_to_a_long_random_string

# Admin account (change before first run)
ADMIN_USERNAME=admin
ADMIN_PASSWORD=StrongPassword123!
ADMIN_EMAIL=admin@yourdomain.com

# Session timeout in hours (default: 8)
SESSION_TIMEOUT_HOURS=8

# Firebase (leave blank to use local file storage)
FIREBASE_CREDENTIALS=path/to/serviceAccountKey.json

# CORS — set to your frontend origin in production
ALLOWED_ORIGINS=http://localhost:5173

# Flask env
FLASK_ENV=development
```

### 3 · Install frontend

```bash
cd CHCAPP
npm install       # or: yarn install
cd ..
```

### 4 · Run (recommended — starts both together)

```bash
python dev_runner.py
```

| Service | URL |
|---|---|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:5000 |

Or run them separately:

```bash
# Terminal 1 — backend
python app.py

# Terminal 2 — frontend
cd CHCAPP && npm run dev
```

---

## 📖 How to Use

### Upload a File

1. Log in and go to **Upload**
2. Select a file (max 16 MB)
3. Add comma-separated **Authorized Users** (optional)
4. Click **Upload** — the file is encrypted and stored immediately

### View & Manage Files

- **Files** page lists all uploads with owner, block hash, and timestamp
- Click **Security** for the full blockchain audit trail
- Click **Decrypt** to download a decrypted copy

### Decrypt a File

1. Click **Decrypt** on any file you have access to
2. Confirm your username and submit
3. The plaintext file downloads automatically

> Unauthorized attempts are blocked **and** logged to the blockchain.

---

## 🔐 Security Model

### CHC Algorithm

```
For each 32-byte block i:
  keystream  = HMAC-SHA256(state, i)
  ciphertext = plaintext  XOR keystream[:len(block)]
  state      = HMAC-SHA256(state, ciphertext_block)
```

Each block's state depends on all previous ciphertext — compromising one block does not reveal earlier plaintext (**forward security**).

### Key Derivation

```
owner_secret  →  stored encrypted with system Fernet key (survives restarts)
seed          =  HMAC-SHA256(owner_secret, block_hash ‖ timestamp ‖ file_id)
user_key      =  HMAC-SHA256(PBKDF2_hash(password), username ‖ ":" ‖ file_id)
wrapped_seed  =  Fernet.encrypt(seed, user_key)   ← authenticated encryption
```

### What's Hardened (recent updates)

| Issue | Fix applied |
|---|---|
| User keys were derivable from public data | Keys now keyed by PBKDF2 password hash |
| Seed wrapping used unauthenticated XOR | Replaced with Fernet (AES-128-CBC + HMAC) |
| Owner secrets lost on server restart | Encrypted & persisted to key vault on disk |
| Sessions never expired | Configurable timeout via `SESSION_TIMEOUT_HOURS` |

---

## 📊 API Reference

### Auth

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/register` | Register a new user |
| `POST` | `/api/login` | Login, returns `session_token` |
| `POST` | `/api/logout` | Invalidate session |
| `GET` | `/api/auth/check` | Check session validity |

### Files

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/upload` | Upload + encrypt a file |
| `GET` | `/api/files` | List all files |
| `POST` | `/api/decrypt/<file_id>` | Decrypt + download a file |
| `GET` | `/api/security/<file_id>` | Get audit trail for a file |

### Blockchain

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/blockchain` | Full blockchain data |
| `GET` | `/api/ping` | Health check |

All protected endpoints require:
```
Authorization: Bearer <session_token>
```

---

## ⚙️ Performance

| Operation | Speed |
|---|---|
| Encryption | ~315 KB/s |
| Decryption | ~630 KB/s |
| Small file round-trip | < 1 ms |
| Storage overhead | Minimal (stream cipher) |

---

## 🧪 Manual Testing Checklist

Automated tests are not yet included. Verify the core workflow manually:

```bash
# 1. Start the app
python dev_runner.py

# 2. In the browser:
#    a) Register two users (e.g. alice, bob)
#    b) Log in as alice, upload a file — add bob as an authorized user
#    c) Log in as bob, decrypt the file ✓
#    d) Log in as a third user (carol) and attempt to decrypt → Access denied ✓
#    e) Check /blockchain — both events should be logged ✓
```

---

## 🚨 Troubleshooting

**Upload fails**
- File must be under 16 MB
- Check Firebase credentials in `.env`
- Ensure `uploads/` directory exists (created automatically on start)

**Decryption fails with "No key found"**
- The requesting user must be the owner or in the authorized list
- If files were uploaded before the latest security update, re-upload them (old wrapped seeds are incompatible)

**Sessions expire unexpectedly**
- Increase `SESSION_TIMEOUT_HOURS` in `.env`

**Frontend can't reach the API**
- Confirm Flask is running on port 5000
- Check `ALLOWED_ORIGINS` matches your frontend URL

**Owner secrets missing after restart**
- Ensure `secure_storage/key_vault/.master.key` exists and is readable
- Run `python app.py` once to let `KeyManager` initialise it

---

## 🔮 Future Enhancements

- [ ] Real blockchain integration (Ethereum / Hyperledger)
- [ ] PostgreSQL / MongoDB for user & session storage
- [ ] AWS S3 / Google Cloud Storage backend
- [ ] Periodic key rotation
- [ ] Group-based hierarchical permissions
- [ ] Large file chunking support
- [ ] HSM integration for master key storage
- [ ] Multi-factor authentication
- [ ] File versioning

---

## 📄 License

This project is for **educational and research purposes**. It demonstrates advanced cryptographic concepts — contextual encryption, blockchain-backed access control, and authenticated key wrapping — in a practical, runnable system.

---

## 🤝 Contributing

Academic project — open for research collaboration and educational use.  
Found a security issue? Please report it responsibly.

---

<div align="center">

**Built with Flask · React · TypeScript · HMAC-SHA256 · Fernet**

*Secure your files. Trust the chain.*

</div>
