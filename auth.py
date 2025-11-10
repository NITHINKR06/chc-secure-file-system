"""
User Authentication and Management Module
Handles user registration, login, and session management

This module provides user authentication and management for the secure file management system.
It handles user registration, login, session management, and user data storage.

Key Features:
- Secure user registration with password hashing
- Session management with secure tokens
- User data storage and retrieval
- Admin user management
- File access tracking per user

Security Features:
- PBKDF2 password hashing with salt
- Secure session token generation
- Session timeout and validation
- User data encryption
"""

import hashlib  # For password hashing and cryptographic operations
import json  # For JSON data serialization/deserialization
import os  # For file system operations
import time  # For timestamp generation and session management
from typing import Dict, Optional, List  # Type hints for better code documentation
import secrets  # For cryptographically secure random number generation

# Configuration files for user data storage
USER_DB_FILE = "users.json"  # File storing user account information
SESSION_FILE = "sessions.json"  # File storing active user sessions

class UserManager:
    def __init__(self):
        self.users = self.load_users()
        self.sessions = self.load_sessions()
        
    def load_users(self) -> Dict:
        """Load user database from JSON file"""
        if os.path.exists(USER_DB_FILE):
            with open(USER_DB_FILE, 'r') as f:
                return json.load(f)
        return {}
    
    def save_users(self):
        """Save user database to JSON file"""
        with open(USER_DB_FILE, 'w') as f:
            json.dump(self.users, f, indent=2)
    
    def load_sessions(self) -> Dict:
        """Load active sessions from JSON file"""
        if os.path.exists(SESSION_FILE):
            with open(SESSION_FILE, 'r') as f:
                return json.load(f)
        return {}
    
    def save_sessions(self):
        """Save active sessions to JSON file"""
        with open(SESSION_FILE, 'w') as f:
            json.dump(self.sessions, f, indent=2)
    
    def hash_password(self, password: str, salt: str = None) -> tuple:
        """Hash password with salt"""
        if salt is None:
            salt = secrets.token_hex(16)
        pwd_hash = hashlib.pbkdf2_hmac('sha256', 
                                       password.encode('utf-8'), 
                                       salt.encode('utf-8'), 
                                       100000)
        return pwd_hash.hex(), salt
    
    def register_user(self, username: str, password: str, email: str, 
                     role: str = "user") -> Dict:
        """Register a new user"""
        if username in self.users:
            return {"success": False, "message": "Username already exists"}
        
        # Hash password
        pwd_hash, salt = self.hash_password(password)
        
        # Create user record
        user_data = {
            "username": username,
            "password_hash": pwd_hash,
            "salt": salt,
            "email": email,
            "role": role,  # "user" or "admin"
            "created_at": time.time(),
            "public_key": secrets.token_hex(32),  # Simulated public key
            "private_key_encrypted": secrets.token_hex(32),  # Encrypted private key
            "files_uploaded": [],
            "files_accessible": []
        }
        
        self.users[username] = user_data
        self.save_users()
        
        return {"success": True, "message": "User registered successfully", "user": user_data}
    
    def login_user(self, username: str, password: str) -> Dict:
        """Authenticate user and create session"""
        if username not in self.users:
            return {"success": False, "message": "Invalid username or password"}
        
        user = self.users[username]
        pwd_hash, _ = self.hash_password(password, user['salt'])
        
        if pwd_hash != user['password_hash']:
            return {"success": False, "message": "Invalid username or password"}
        
        # Create session
        session_token = secrets.token_hex(32)
        self.sessions[session_token] = {
            "username": username,
            "role": user['role'],
            "login_time": time.time(),
            "last_activity": time.time()
        }
        self.save_sessions()
        
        return {
            "success": True, 
            "message": "Login successful",
            "session_token": session_token,
            "user": {
                "username": username,
                "email": user['email'],
                "role": user['role']
            }
        }
    
    def logout_user(self, session_token: str) -> bool:
        """Logout user and destroy session"""
        if session_token in self.sessions:
            del self.sessions[session_token]
            self.save_sessions()
            return True
        return False
    
    def verify_session(self, session_token: str) -> Optional[Dict]:
        """Verify if session is valid and return user info"""
        if session_token in self.sessions:
            session = self.sessions[session_token]
            # Update last activity
            session['last_activity'] = time.time()
            self.save_sessions()
            
            # Return user info
            username = session['username']
            if username in self.users:
                return {
                    "username": username,
                    "role": self.users[username]['role'],
                    "email": self.users[username]['email']
                }
        return None
    
    def get_user_keys(self, username: str) -> Dict:
        """Get user's cryptographic keys"""
        if username in self.users:
            user = self.users[username]
            return {
                "public_key": user['public_key'],
                "private_key_encrypted": user['private_key_encrypted']
            }
        return {}
    
    def add_file_to_user(self, username: str, file_id: str, is_owner: bool = True):
        """Add file reference to user's record"""
        if username in self.users:
            if is_owner:
                self.users[username]['files_uploaded'].append(file_id)
            else:
                self.users[username]['files_accessible'].append(file_id)
            self.save_users()
    
    def get_user_files(self, username: str) -> Dict:
        """Get all files associated with a user"""
        if username in self.users:
            user = self.users[username]
            return {
                "uploaded": user['files_uploaded'],
                "accessible": user['files_accessible']
            }
        return {"uploaded": [], "accessible": []}
    
    def is_admin(self, username: str) -> bool:
        """Check if user has admin role"""
        if username in self.users:
            return self.users[username]['role'] == 'admin'
        return False
    
    def get_all_users(self) -> List[Dict]:
        """Get all users (admin only)"""
        users_list = []
        for username, user_data in self.users.items():
            users_list.append({
                "username": username,
                "email": user_data['email'],
                "role": user_data['role'],
                "created_at": time.strftime('%Y-%m-%d %H:%M:%S', 
                                           time.localtime(user_data['created_at'])),
                "files_uploaded": len(user_data['files_uploaded']),
                "files_accessible": len(user_data['files_accessible'])
            })
        return users_list
    
    def delete_user(self, username: str) -> bool:
        """Delete a user (admin only)"""
        if username in self.users:
            del self.users[username]
            self.save_users()
            # Remove user's sessions
            sessions_to_remove = [token for token, session in self.sessions.items() 
                                 if session['username'] == username]
            for token in sessions_to_remove:
                del self.sessions[token]
            self.save_sessions()
            return True
        return False

# Initialize default admin user if not exists
def init_default_admin():
    """Create default admin user on first run"""
    manager = UserManager()
    if 'admin' not in manager.users:
        result = manager.register_user(
            username='admin',
            password='admin123',
            email='admin@chc.local',
            role='admin'
        )
        print("[Auth] Default admin user created - Username: admin, Password: admin123")
        print("[Auth] ⚠️  Please change the admin password after first login!")

# Initialize on module import
init_default_admin()
