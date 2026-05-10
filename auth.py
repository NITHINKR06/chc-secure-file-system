"""
User Authentication and Management Module
Handles user registration, login, and session management

CHANGES FROM ORIGINAL:
  1. SESSION_TIMEOUT_SECONDS added (default 8 hours, overridable via env var
     SESSION_TIMEOUT_HOURS).  verify_session() now checks last_activity and
     expires stale sessions automatically.
  2. purge_expired_sessions() helper cleans up the session file.
  3. get_user_password_hash() helper added so encryption.generate_user_key()
     can receive the stored password hash without exposing the full user dict.
"""

import hashlib
import json
import os
import time
from typing import Dict, Optional, List
import secrets
from dotenv import load_dotenv

load_dotenv()

USER_DB_FILE = "users.json"
SESSION_FILE = "sessions.json"

# FIX 4 — Configurable session timeout (default: 8 hours)
SESSION_TIMEOUT_SECONDS = int(os.getenv("SESSION_TIMEOUT_HOURS", "8")) * 3600


class UserManager:
    def __init__(self):
        self.users = self.load_users()
        self.sessions = self.load_sessions()

    # ------------------------------------------------------------------
    # Persistence helpers
    # ------------------------------------------------------------------

    def load_users(self) -> Dict:
        """Load user database from JSON file."""
        if os.path.exists(USER_DB_FILE):
            with open(USER_DB_FILE, "r") as f:
                return json.load(f)
        return {}

    def save_users(self):
        """Save user database to JSON file."""
        with open(USER_DB_FILE, "w") as f:
            json.dump(self.users, f, indent=2)

    def load_sessions(self) -> Dict:
        """Load active sessions from JSON file."""
        if os.path.exists(SESSION_FILE):
            with open(SESSION_FILE, "r") as f:
                return json.load(f)
        return {}

    def save_sessions(self):
        """Save active sessions to JSON file."""
        with open(SESSION_FILE, "w") as f:
            json.dump(self.sessions, f, indent=2)

    # ------------------------------------------------------------------
    # Password helpers
    # ------------------------------------------------------------------

    def hash_password(self, password: str, salt: str = None) -> tuple:
        """Hash password with PBKDF2-SHA256 and a random salt."""
        if salt is None:
            salt = secrets.token_hex(16)
        pwd_hash = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000
        )
        return pwd_hash.hex(), salt

    # ------------------------------------------------------------------
    # NEW helper — used by encryption.generate_user_key()
    # ------------------------------------------------------------------

    def get_user_password_hash(self, username: str) -> Optional[str]:
        """
        Return the stored PBKDF2 password hash hex string for a user,
        or None if the user does not exist.

        This is intentionally kept as a separate method so callers never
        need to inspect the full user dict.
        """
        user = self.users.get(username)
        if user:
            return user.get("password_hash")
        return None

    # ------------------------------------------------------------------
    # Registration / login / logout
    # ------------------------------------------------------------------

    def register_user(self, username: str, password: str, email: str,
                      role: str = "user") -> Dict:
        """Register a new user."""
        if username in self.users:
            return {"success": False, "message": "Username already exists"}

        pwd_hash, salt = self.hash_password(password)

        user_data = {
            "username": username,
            "password_hash": pwd_hash,
            "salt": salt,
            "email": email,
            "role": role,
            "created_at": time.time(),
            "public_key": secrets.token_hex(32),
            "private_key_encrypted": secrets.token_hex(32),
            "files_uploaded": [],
            "files_accessible": [],
        }

        self.users[username] = user_data
        self.save_users()
        return {"success": True, "message": "User registered successfully", "user": user_data}

    def login_user(self, username: str, password: str) -> Dict:
        """Authenticate user and create a session."""
        if username not in self.users:
            return {"success": False, "message": "Invalid username or password"}

        user = self.users[username]
        pwd_hash, _ = self.hash_password(password, user["salt"])

        if pwd_hash != user["password_hash"]:
            return {"success": False, "message": "Invalid username or password"}

        session_token = secrets.token_hex(32)
        now = time.time()
        self.sessions[session_token] = {
            "username": username,
            "role": user["role"],
            "login_time": now,
            "last_activity": now,
        }
        self.save_sessions()

        return {
            "success": True,
            "message": "Login successful",
            "session_token": session_token,
            "user": {
                "username": username,
                "email": user["email"],
                "role": user["role"],
            },
        }

    def logout_user(self, session_token: str) -> bool:
        """Logout user and destroy session."""
        if session_token in self.sessions:
            del self.sessions[session_token]
            self.save_sessions()
            return True
        return False

    # ------------------------------------------------------------------
    # FIX 4 — verify_session now enforces timeout
    # ------------------------------------------------------------------

    def verify_session(self, session_token: str) -> Optional[Dict]:
        """
        Verify if a session is valid and return user info.

        CHANGE: sessions that have been inactive for longer than
        SESSION_TIMEOUT_SECONDS are automatically expired and removed.
        """
        session = self.sessions.get(session_token)
        if not session:
            return None

        now = time.time()
        idle_seconds = now - session.get("last_activity", 0)

        if idle_seconds > SESSION_TIMEOUT_SECONDS:
            # Session has timed out — remove it
            del self.sessions[session_token]
            self.save_sessions()
            return None

        # Still valid — refresh last_activity
        session["last_activity"] = now
        self.save_sessions()

        username = session["username"]
        if username in self.users:
            return {
                "username": username,
                "role": self.users[username]["role"],
                "email": self.users[username]["email"],
            }
        return None

    # ------------------------------------------------------------------
    # NEW helper — clean up all expired sessions at once
    # ------------------------------------------------------------------

    def purge_expired_sessions(self) -> int:
        """
        Remove all sessions that have exceeded SESSION_TIMEOUT_SECONDS.
        Returns the number of sessions removed.
        Call this periodically (e.g. on startup or via a scheduled job).
        """
        now = time.time()
        expired = [
            token
            for token, sess in self.sessions.items()
            if now - sess.get("last_activity", 0) > SESSION_TIMEOUT_SECONDS
        ]
        for token in expired:
            del self.sessions[token]
        if expired:
            self.save_sessions()
        return len(expired)

    # ------------------------------------------------------------------
    # Key / file / admin helpers (unchanged)
    # ------------------------------------------------------------------

    def get_user_keys(self, username: str) -> Dict:
        """Get user's cryptographic keys."""
        if username in self.users:
            user = self.users[username]
            return {
                "public_key": user["public_key"],
                "private_key_encrypted": user["private_key_encrypted"],
            }
        return {}

    def add_file_to_user(self, username: str, file_id: str, is_owner: bool = True):
        """Add file reference to user's record."""
        if username in self.users:
            key = "files_uploaded" if is_owner else "files_accessible"
            self.users[username][key].append(file_id)
            self.save_users()

    def get_user_files(self, username: str) -> Dict:
        """Get all files associated with a user."""
        if username in self.users:
            user = self.users[username]
            return {
                "uploaded": user["files_uploaded"],
                "accessible": user["files_accessible"],
            }
        return {"uploaded": [], "accessible": []}

    def is_admin(self, username: str) -> bool:
        """Check if user has admin role."""
        if username in self.users:
            return self.users[username]["role"] == "admin"
        return False

    def get_all_users(self) -> List[Dict]:
        """Get all users (admin only)."""
        return [
            {
                "username": username,
                "email": data["email"],
                "role": data["role"],
                "created_at": time.strftime(
                    "%Y-%m-%d %H:%M:%S", time.localtime(data["created_at"])
                ),
                "files_uploaded": len(data["files_uploaded"]),
                "files_accessible": len(data["files_accessible"]),
            }
            for username, data in self.users.items()
        ]

    def delete_user(self, username: str) -> bool:
        """Delete a user (admin only)."""
        if username in self.users:
            del self.users[username]
            self.save_users()
            stale = [t for t, s in self.sessions.items() if s["username"] == username]
            for token in stale:
                del self.sessions[token]
            self.save_sessions()
            return True
        return False


# ---------------------------------------------------------------------------
# Default admin initialisation (unchanged)
# ---------------------------------------------------------------------------

def init_default_admin():
    """Create default admin user on first run."""
    manager = UserManager()
    # Purge stale sessions on every startup
    purged = manager.purge_expired_sessions()
    if purged:
        print(f"[Auth] Purged {purged} expired session(s) on startup.")

    if "admin" not in manager.users:
        admin_username = os.getenv("ADMIN_USERNAME", "admin")
        admin_password = os.getenv("ADMIN_PASSWORD", "admin123")
        admin_email = os.getenv("ADMIN_EMAIL", "admin@chc.local")

        manager.register_user(
            username=admin_username,
            password=admin_password,
            email=admin_email,
            role="admin",
        )
        print(f"[Auth] Default admin user created — Username: {admin_username}")
        if admin_password == "admin123":
            print("[Auth] ⚠️  WARNING: Using default admin password! "
                  "Set ADMIN_PASSWORD env var to change it.")


init_default_admin()
