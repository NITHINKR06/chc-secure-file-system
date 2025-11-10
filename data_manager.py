"""
Data Storage and Management Module
Handles secure storage of files, keys, and metadata using Firestore

This module manages the "off-chain" storage component of the secure file management system.
It provides secure storage for encrypted files, user keys, and metadata with integrity verification.

Key Features:
- Secure encrypted file storage in Firestore
- Metadata management with integrity verification
- Key vault for secure key storage in Firestore
- Backup and recovery functionality
- File integrity verification
- Secure deletion capabilities

The module implements the off-chain storage requirements:
- Encrypted files stored securely in Firestore (base64 encoded)
- Metadata with checksums for integrity in Firestore
- User keys stored in encrypted key vault in Firestore
- Backup and recovery mechanisms

Note: Firestore document size limit is 1MB. For files larger than ~750KB (after base64 encoding),
consider using Firebase Cloud Storage for the encrypted files and storing only references in Firestore.
"""

import os  # For file system operations and environment variables
import json  # For JSON data serialization/deserialization
import time  # For timestamp generation
from typing import Dict, List, Optional  # Type hints for better code documentation
from cryptography.fernet import Fernet  # For symmetric encryption of keys
import base64  # For base64 encoding/decoding of keys and files
import hashlib  # For SHA256 hash calculations and integrity verification

# Firebase Admin SDK imports
try:
    import firebase_admin
    from firebase_admin import credentials, firestore, storage as firebase_storage
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False
    print("[DataManager] WARNING: firebase-admin not installed. Install with: pip install firebase-admin")

# Firestore collection names
ENCRYPTED_FILES_COLLECTION = "encrypted_files"
METADATA_COLLECTION = "metadata"
KEY_VAULT_COLLECTION = "key_vault"
MASTER_KEYS_COLLECTION = "master_keys"
BACKUPS_COLLECTION = "backups"

class DataManager:
    def __init__(self):
        """Initialize data manager with Firestore client"""
        # Initialize Firestore
        self.db = self._init_firestore()
        
        # Load or create master key (stored in Firestore)
        self.master_key = self.load_or_create_master_key()
        self.fernet = Fernet(self.master_key)
        
        print("[DataManager] Initialized with Firestore storage")
    
    def _init_firestore(self):
        """Initialize Firestore client"""
        if not FIREBASE_AVAILABLE:
            raise ImportError("firebase-admin is not installed. Please install it with: pip install firebase-admin")
        
        try:
            # Check if Firebase app is already initialized
            firebase_admin.get_app()
            print("[DataManager] Using existing Firebase app instance")
        except ValueError:
            # Initialize Firebase app
            # Option 1: Use service account key file (recommended for production)
            # Set environment variable: GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
            credential_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
            
            if credential_path:
                # Environment variable is set, check if file exists
                if os.path.exists(credential_path):
                    try:
                        cred = credentials.Certificate(credential_path)
                        firebase_admin.initialize_app(cred)
                        print(f"[DataManager] Firebase initialized with service account: {credential_path}")
                    except Exception as e:
                        print(f"[DataManager] ERROR: Failed to initialize Firebase with service account file")
                        print(f"[DataManager] File: {credential_path}")
                        print(f"[DataManager] Error: {e}")
                        print("\n[DataManager] Please check:")
                        print("  1. The file exists and is readable")
                        print("  2. The file is valid JSON")
                        print("  3. The file contains valid service account credentials")
                        raise
                else:
                    # Environment variable is set but file doesn't exist
                    print(f"[DataManager] ERROR: Service account file not found")
                    print(f"[DataManager] Expected file: {credential_path}")
                    print(f"\n[DataManager] To fix this:")
                    print("  1. Download service account key from Firebase Console:")
                    print("     https://console.firebase.google.com/project/chcs-2f71d/settings/serviceaccounts/adminsdk")
                    print("  2. Save it as: firebase-service-account.json")
                    print(f"  3. Place it in: {os.path.dirname(credential_path)}")
                    print("\n[DataManager] Or set the environment variable to the correct path:")
                    print(f"  PowerShell: $env:GOOGLE_APPLICATION_CREDENTIALS = 'path/to/firebase-service-account.json'")
                    raise FileNotFoundError(f"Service account file not found: {credential_path}")
            else:
                # No environment variable set, try Application Default Credentials
                try:
                    firebase_admin.initialize_app()
                    print("[DataManager] Firebase initialized with Application Default Credentials")
                except Exception as e:
                    print(f"[DataManager] ERROR: Firebase initialization failed: {e}")
                    print("\n[DataManager] To fix this:")
                    print("  1. Download service account key from Firebase Console:")
                    print("     https://console.firebase.google.com/project/chcs-2f71d/settings/serviceaccounts/adminsdk")
                    print("  2. Save it as: firebase-service-account.json in your project directory")
                    print("  3. Set environment variable:")
                    print("     PowerShell: $env:GOOGLE_APPLICATION_CREDENTIALS = '<path-to-firebase-service-account.json>'")
                    print("     Or set it in your system environment variables")
                    raise
        
        # Get Firestore client
        try:
            db = firestore.client()
            return db
        except Exception as e:
            print(f"[DataManager] ERROR: Failed to create Firestore client: {e}")
            print("[DataManager] Please check your Firebase configuration and try again")
            raise
    
    def load_or_create_master_key(self) -> bytes:
        """Load or create master encryption key for key vault from Firestore"""
        master_key_ref = self.db.collection(MASTER_KEYS_COLLECTION).document('master_key')
        master_key_doc = master_key_ref.get()
        
        if master_key_doc.exists:
            # Load existing master key
            key_data = master_key_doc.to_dict()
            master_key_b64 = key_data.get('key')
            master_key = base64.b64decode(master_key_b64)
            print("[DataManager] Loaded existing master key from Firestore")
            return master_key
        else:
            # Generate new master key
            key = Fernet.generate_key()
            key_b64 = base64.b64encode(key).decode()
            
            # Store in Firestore
            master_key_ref.set({
                'key': key_b64,
                'created_at': time.time(),
                'updated_at': time.time()
            })
            
            print("[DataManager] Generated new master key and stored in Firestore")
            return key
    
    def store_encrypted_file(self, file_id: str, encrypted_data: bytes, 
                           original_name: str, block_hash: str = None, 
                           owner: str = None, authorized_users: list = None) -> Dict:
        """
        Store encrypted file with enhanced metadata in Firestore
        
        Note: Firestore has a 1MB document size limit. Encrypted files are stored as base64 strings.
        For files larger than ~750KB (after encryption and base64 encoding), consider chunking
        or using Firebase Cloud Storage and storing only the reference here.
        """
        # Check if file is too large for Firestore (1MB limit, but base64 adds ~33% overhead)
        # Leave some margin: ~700KB raw data = ~933KB base64 = safe for 1MB limit
        if len(encrypted_data) > 700 * 1024:
            print(f"[DataManager] WARNING: File {file_id} is large ({len(encrypted_data)} bytes). "
                  f"Consider using Firebase Cloud Storage for files > 700KB.")
        
        # Encode encrypted data as base64 for Firestore storage
        encrypted_data_b64 = base64.b64encode(encrypted_data).decode('utf-8')
        
        # Calculate checksum
        checksum = hashlib.sha256(encrypted_data).hexdigest()
        
        # Store enhanced metadata
        metadata = {
            "file_id": file_id,
            "original_name": original_name,
            "encrypted_data": encrypted_data_b64,  # Store encrypted file as base64 in Firestore
            "size_encrypted": len(encrypted_data),
            "storage_time": time.time(),
            "checksum": checksum,
            "block_hash": block_hash,
            "owner": owner,
            "authorized_users": authorized_users or [],
            "storage_type": "firestore_encrypted",
            "encryption_method": "CHC"
        }
        
        # Store metadata document in Firestore
        metadata_ref = self.db.collection(METADATA_COLLECTION).document(file_id)
        metadata_ref.set(metadata)
        
        print(f"[DataManager] Stored encrypted file in Firestore: {file_id}")
        print(f"[DataManager] Firestore collection: {METADATA_COLLECTION}")
        print(f"[DataManager] Document ID: {file_id}")
        
        return metadata
    
    def retrieve_encrypted_file(self, file_id: str) -> Optional[bytes]:
        """Retrieve encrypted file data from Firestore"""
        # Get metadata document from Firestore
        metadata_ref = self.db.collection(METADATA_COLLECTION).document(file_id)
        metadata_doc = metadata_ref.get()
        
        if not metadata_doc.exists:
            print(f"[DataManager] File metadata not found in Firestore: {file_id}")
            return None
        
        metadata = metadata_doc.to_dict()
        encrypted_data_b64 = metadata.get('encrypted_data')
        
        if not encrypted_data_b64:
            print(f"[DataManager] Encrypted data not found in metadata: {file_id}")
            return None
        
        # Decode base64 to get encrypted bytes
        try:
            encrypted_data = base64.b64decode(encrypted_data_b64)
        except Exception as e:
            print(f"[DataManager] Error decoding base64 data: {e}")
            return None
        
        # Verify checksum
        stored_checksum = metadata.get('checksum')
        if stored_checksum:
            current_checksum = hashlib.sha256(encrypted_data).hexdigest()
            if current_checksum != stored_checksum:
                print(f"[DataManager] WARNING: Checksum mismatch for file {file_id}")
                return None
        
        print(f"[DataManager] Retrieved encrypted file from Firestore: {file_id}")
        return encrypted_data
    
    def retrieve_file_metadata(self, file_id: str) -> Optional[Dict]:
        """Retrieve file metadata from Firestore"""
        metadata_ref = self.db.collection(METADATA_COLLECTION).document(file_id)
        metadata_doc = metadata_ref.get()
        
        if metadata_doc.exists:
            metadata = metadata_doc.to_dict()
            # Remove encrypted_data from metadata response (it's large, use retrieve_encrypted_file instead)
            if 'encrypted_data' in metadata:
                metadata_copy = metadata.copy()
                del metadata_copy['encrypted_data']
                metadata = metadata_copy
            print(f"[DataManager] Retrieved metadata from Firestore: {file_id}")
            return metadata
        return None
    
    def verify_file_integrity(self, file_id: str) -> bool:
        """Verify file integrity by checking checksum"""
        # Retrieve encrypted file (which also verifies checksum)
        encrypted_data = self.retrieve_encrypted_file(file_id)
        if not encrypted_data:
            return False
        
        # Get metadata to verify checksum
        metadata = self.retrieve_file_metadata(file_id)
        if not metadata:
            return False
        
        # Verify checksum (already done in retrieve_encrypted_file, but double-check)
        current_checksum = hashlib.sha256(encrypted_data).hexdigest()
        stored_checksum = metadata.get('checksum')
        
        if current_checksum != stored_checksum:
            print(f"[DataManager] Integrity check failed for file {file_id}")
            return False
        
        print(f"[DataManager] Integrity check passed for file {file_id}")
        return True
    
    def store_wrapped_seed(self, file_id: str, user: str, wrapped_seed: bytes):
        """Store wrapped seed in secure key vault in Firestore"""
        # Encrypt the wrapped seed with master key
        encrypted_seed = self.fernet.encrypt(wrapped_seed)
        encrypted_seed_b64 = base64.b64encode(encrypted_seed).decode('utf-8')
        
        # Store in Firestore key vault collection
        seed_doc_id = f"{file_id}_{user}"
        seed_ref = self.db.collection(KEY_VAULT_COLLECTION).document(seed_doc_id)
        seed_ref.set({
            'file_id': file_id,
            'user': user,
            'encrypted_seed': encrypted_seed_b64,
            'created_at': time.time(),
            'updated_at': time.time()
        })
        
        print(f"[DataManager] Stored wrapped seed in Firestore for {user} -> {file_id}")
    
    def retrieve_wrapped_seed(self, file_id: str, user: str) -> Optional[bytes]:
        """Retrieve wrapped seed from secure key vault in Firestore"""
        seed_doc_id = f"{file_id}_{user}"
        seed_ref = self.db.collection(KEY_VAULT_COLLECTION).document(seed_doc_id)
        seed_doc = seed_ref.get()
        
        if not seed_doc.exists:
            return None
        
        seed_data = seed_doc.to_dict()
        encrypted_seed_b64 = seed_data.get('encrypted_seed')
        
        if not encrypted_seed_b64:
            return None
        
        try:
            # Decode base64
            encrypted_seed = base64.b64decode(encrypted_seed_b64)
            # Decrypt with master key
            wrapped_seed = self.fernet.decrypt(encrypted_seed)
            return wrapped_seed
        except Exception as e:
            print(f"[DataManager] Error decrypting seed: {e}")
            return None
    
    def delete_file_data(self, file_id: str) -> bool:
        """Securely delete all data related to a file from Firestore"""
        deleted = False
        
        # Delete metadata document (which contains the encrypted file)
        metadata_ref = self.db.collection(METADATA_COLLECTION).document(file_id)
        if metadata_ref.get().exists:
            metadata_ref.delete()
            deleted = True
        
        # Delete all wrapped seeds for this file
        seeds_query = self.db.collection(KEY_VAULT_COLLECTION).where('file_id', '==', file_id)
        seeds = seeds_query.stream()
        
        for seed_doc in seeds:
            seed_doc.reference.delete()
        
        if deleted:
            print(f"[DataManager] Deleted file data from Firestore: {file_id}")
        
        return deleted
    
    def create_backup(self, backup_name: str = None) -> str:
        """Create backup of all data in Firestore"""
        if backup_name is None:
            backup_name = f"backup_{time.strftime('%Y%m%d_%H%M%S')}"
        
        backup_data = {
            'backup_name': backup_name,
            'backup_time': time.time(),
            'files': [],
            'seeds': [],
            'metadata_count': 0
        }
        
        # Backup metadata (files)
        metadata_docs = self.db.collection(METADATA_COLLECTION).stream()
        for doc in metadata_docs:
            file_data = doc.to_dict()
            # Remove encrypted_data to reduce backup size (can be regenerated)
            if 'encrypted_data' in file_data:
                file_data_backup = file_data.copy()
                del file_data_backup['encrypted_data']
                backup_data['files'].append(file_data_backup)
            else:
                backup_data['files'].append(file_data)
            backup_data['metadata_count'] += 1
        
        # Backup wrapped seeds
        seeds_docs = self.db.collection(KEY_VAULT_COLLECTION).stream()
        for doc in seeds_docs:
            backup_data['seeds'].append(doc.to_dict())
        
        # Store backup in Firestore
        backup_ref = self.db.collection(BACKUPS_COLLECTION).document(backup_name)
        backup_ref.set(backup_data)
        
        print(f"[DataManager] Created backup in Firestore: {backup_name}")
        print(f"[DataManager] Backed up {backup_data['metadata_count']} files and {len(backup_data['seeds'])} seeds")
        
        return backup_name
    
    def restore_backup(self, backup_name: str) -> bool:
        """Restore data from backup in Firestore"""
        backup_ref = self.db.collection(BACKUPS_COLLECTION).document(backup_name)
        backup_doc = backup_ref.get()
        
        if not backup_doc.exists:
            print(f"[DataManager] Backup not found in Firestore: {backup_name}")
            return False
        
        backup_data = backup_doc.to_dict()
        
        # Note: Full restore would require the encrypted_data which we don't store in backup
        # This is a metadata-only restore. For full restore, you'd need to keep encrypted_data in backup.
        print(f"[DataManager] WARNING: Restore from backup is metadata-only. "
              f"Encrypted file data is not included in backups to save space.")
        print(f"[DataManager] To fully restore, you need to re-upload files or include encrypted_data in backups.")
        
        return True
    
    def get_storage_statistics(self) -> Dict:
        """Get storage usage statistics from Firestore"""
        stats = {
            "total_files": 0,
            "total_size": 0,
            "encrypted_files": 0,
            "wrapped_seeds": 0,
            "backups": 0,
            "storage_type": "firestore"
        }
        
        # Count metadata documents (files)
        metadata_docs = self.db.collection(METADATA_COLLECTION).stream()
        for doc in metadata_docs:
            file_data = doc.to_dict()
            stats["encrypted_files"] += 1
            stats["total_files"] += 1
            stats["total_size"] += file_data.get('size_encrypted', 0)
        
        # Count wrapped seeds
        seeds_docs = self.db.collection(KEY_VAULT_COLLECTION).stream()
        for doc in seeds_docs:
            stats["wrapped_seeds"] += 1
        
        # Count backups
        backups_docs = self.db.collection(BACKUPS_COLLECTION).stream()
        for doc in backups_docs:
            stats["backups"] += 1
        
        stats["total_size_mb"] = round(stats["total_size"] / (1024 * 1024), 2)
        
        return stats
    
    def cleanup_old_files(self, days_old: int = 30) -> int:
        """Clean up files older than specified days from Firestore"""
        current_time = time.time()
        cutoff_time = current_time - (days_old * 24 * 60 * 60)
        deleted_count = 0
        
        # Query for old files
        metadata_docs = self.db.collection(METADATA_COLLECTION).stream()
        for doc in metadata_docs:
            file_data = doc.to_dict()
            storage_time = file_data.get('storage_time', 0)
            
            if storage_time < cutoff_time:
                file_id = file_data.get('file_id')
                if file_id and self.delete_file_data(file_id):
                    deleted_count += 1
        
        print(f"[DataManager] Cleaned up {deleted_count} old files from Firestore")
        return deleted_count

class KeyManager:
    """Secure key management for user keys and master secrets using Firestore"""
    
    def __init__(self):
        # Initialize Firestore
        self.use_firestore = False
        try:
            import firebase_admin
            from firebase_admin import firestore
            try:
                # Try to get existing app
                firebase_admin.get_app()
                self.db = firestore.client()
                self.use_firestore = True
                self.user_keys_collection = "user_keys"
            except ValueError:
                # Firebase not initialized, fallback to local
                self.use_firestore = False
        except ImportError:
            # Firebase admin not installed, fallback to local
            self.use_firestore = False
        
        if not self.use_firestore:
            # Fallback to local storage if Firestore not available
            KEY_VAULT_DIR = os.path.join("secure_storage", "key_vault")
            os.makedirs(KEY_VAULT_DIR, exist_ok=True)
            self.key_store_file = os.path.join(KEY_VAULT_DIR, "user_keys.enc")
        
        self.master_key = self.load_or_create_master_key()
        self.fernet = Fernet(self.master_key)
        
    def load_or_create_master_key(self) -> bytes:
        """Load or create master key for user key encryption"""
        if self.use_firestore:
            # Load from Firestore
            key_ref = self.db.collection(MASTER_KEYS_COLLECTION).document('user_master_key')
            key_doc = key_ref.get()
            
            if key_doc.exists:
                key_data = key_doc.to_dict()
                key_b64 = key_data.get('key')
                return base64.b64decode(key_b64)
            else:
                key = Fernet.generate_key()
                key_b64 = base64.b64encode(key).decode()
                key_ref.set({
                    'key': key_b64,
                    'created_at': time.time()
                })
                return key
        else:
            # Fallback to local storage
            import os
            KEY_VAULT_DIR = os.path.join("secure_storage", "key_vault")
            key_file = os.path.join(KEY_VAULT_DIR, ".user_master.key")
            if os.path.exists(key_file):
                with open(key_file, 'rb') as f:
                    return f.read()
            else:
                key = Fernet.generate_key()
                with open(key_file, 'wb') as f:
                    f.write(key)
                return key
    
    def store_user_keys(self, username: str, public_key: bytes, private_key: bytes):
        """Securely store user's key pair"""
        if self.use_firestore:
            # Store in Firestore
            user_key_ref = self.db.collection(self.user_keys_collection).document(username)
            user_key_ref.set({
                'public_key': base64.b64encode(public_key).decode(),
                'private_key': base64.b64encode(private_key).decode(),
                'created_at': time.time(),
                'updated_at': time.time()
            })
        else:
            # Fallback to local storage
            import json
            if os.path.exists(self.key_store_file):
                with open(self.key_store_file, 'rb') as f:
                    encrypted_data = f.read()
                keys_data = json.loads(self.fernet.decrypt(encrypted_data))
            else:
                keys_data = {}
            
            keys_data[username] = {
                "public_key": base64.b64encode(public_key).decode(),
                "private_key": base64.b64encode(private_key).decode(),
                "created_at": time.time()
            }
            
            encrypted_data = self.fernet.encrypt(json.dumps(keys_data).encode())
            with open(self.key_store_file, 'wb') as f:
                f.write(encrypted_data)
    
    def get_user_keys(self, username: str) -> Optional[Dict]:
        """Retrieve user's key pair"""
        if self.use_firestore:
            # Retrieve from Firestore
            user_key_ref = self.db.collection(self.user_keys_collection).document(username)
            user_key_doc = user_key_ref.get()
            
            if user_key_doc.exists:
                key_data = user_key_doc.to_dict()
                return {
                    "public_key": base64.b64decode(key_data["public_key"]),
                    "private_key": base64.b64decode(key_data["private_key"])
                }
            return None
        else:
            # Fallback to local storage
            import json
            if not os.path.exists(self.key_store_file):
                return None
            
            with open(self.key_store_file, 'rb') as f:
                encrypted_data = f.read()
            
            try:
                keys_data = json.loads(self.fernet.decrypt(encrypted_data))
                if username in keys_data:
                    return {
                        "public_key": base64.b64decode(keys_data[username]["public_key"]),
                        "private_key": base64.b64decode(keys_data[username]["private_key"])
                    }
            except Exception as e:
                print(f"[KeyManager] Error retrieving keys: {e}")
            
            return None
