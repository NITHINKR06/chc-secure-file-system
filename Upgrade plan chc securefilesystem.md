# 🔐 CHC Secure File System — Upgrade Plan

## 🌟 Unique Feature to Add: File Revocation System
Right now there's no way to remove a user's access after granting it. Add a **per-user seed invalidation** system — owner can revoke a specific user's wrapped seed without re-encrypting the file for everyone else. This is a real cryptographic engineering problem and very few student projects touch it.

---

## Phase 1 — Fix the Gaps (1–2 weeks)

- [ ] Add **unit tests** using pytest for `encryption.py`, `blockchain.py`, `auth.py`
  - Test: correct decrypt after encrypt, wrong password fails, chain tamper detection
- [ ] Add **MFA via TOTP** (pyotp + qrcode) on login — show QR code, verify 6-digit code
- [ ] Replace "blockchain" label everywhere with **"tamper-evident audit log"** — more accurate, less hype
- [ ] Add **file size limit + MIME type validation** on upload endpoint

---

## Phase 2 — New Unique Features (2–3 weeks)

### 🔑 File Revocation (The Standout Feature)
```
POST /api/revoke/<file_id>/<username>
```
- Deletes that user's wrapped seed entry from the key vault
- Their Fernet key no longer exists — decrypt attempt returns 403
- Event is logged to the audit chain: `REVOKE | owner=alice | target=bob | file=xyz`
- Owner can re-grant access later by re-wrapping a new seed for that user

**Why this is impressive:** Most encryption systems require re-encrypting the entire file to revoke access. CHC's per-user key wrapping design makes targeted revocation possible — this is worth explaining in interviews.

### ⏰ Time-Limited Access Tokens
```
POST /api/grant/<file_id>
Body: { "username": "bob", "expires_in_hours": 24 }
```
- Wrapped seed is stored with an expiry timestamp
- APScheduler background job checks every hour and deletes expired grants
- Expired access attempt returns `403 Access Expired` with timestamp

### ✅ Audit Chain Verifier Endpoint
```
GET /api/blockchain/verify
```
- Recomputes all SHA-256 hashes from genesis block
- Returns: `{ "valid": true, "blocks": 42, "first_tampered_block": null }`
- If tampered: returns the exact block index and hash mismatch details

---

## Phase 3 — Production Hardening (1 week)

- [ ] Migrate from flat JSON to **SQLite via SQLAlchemy** — same simplicity, proper relational DB
- [ ] Add **AES-GCM hybrid mode toggle** — CHC for files < 1 MB, AES-GCM for larger files with a UI note explaining the speed/security tradeoff
- [ ] Add **failed access alert emails** — notify file owner when an unauthorized decrypt is attempted (smtplib)
- [ ] Add **password change flow** — re-derive and re-wrap all user's seed entries when password changes

---

## Resume Line After Upgrades

> "Implemented per-user cryptographic access revocation without file re-encryption, TOTP-based MFA, and time-limited access grants with automated expiry using APScheduler."

---

## Quick Wins (Do These First — Under 1 Day Each)

| Task | Time | Impact |
|---|---|---|
| Add pytest for encryption.py | 2 hrs | Production credibility |
| Replace "blockchain" wording | 30 min | Accuracy, no hype |
| Add audit chain verifier endpoint | 3 hrs | Demonstrable integrity check |
