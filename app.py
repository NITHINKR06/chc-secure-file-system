"""
Flask Web Application for CHC (Contextual Hash Chain) Secure Cloud Storage
Demonstrates blockchain-linked contextual encryption for secure file storage

This is the main web application that implements the complete 7-step secure file management flow:
1. File Upload - User uploads file to system
2. Off-Chain Encryption - System derives seed and encrypts file
3. On-Chain Logging - Blockchain records access control and metadata
4. File Access & Retrieval - System retrieves metadata and ciphertext
5. Authorized User Access - Authorized users decrypt files successfully
6. Unauthorized Prevention - Unauthorized users are blocked
7. Security Outcome - Data confidentiality and integrity maintained
"""

# Import Flask and web framework components
from flask import Flask, render_template, request, redirect, url_for, flash, send_file, jsonify, session
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from functools import wraps  # For decorators
import os  # File system operations
import json  # JSON data handling
import time  # Timestamp generation
import hashlib  # Cryptographic hash functions
from werkzeug.utils import secure_filename  # Secure filename handling
import encryption  # CHC encryption module
import blockchain  # Blockchain management module
from typing import Dict, Optional  # Type hints for better code documentation
import io  # Input/output operations for file handling
import logging  # For proper logging
from dotenv import load_dotenv  # For environment variables

# Load environment variables from .env file
load_dotenv()

# Import custom modules for system functionality
from data_manager import DataManager, KeyManager  # Secure data storage and key management
from auth import UserManager  # User authentication and management

# Configure logging
logging.basicConfig(
    level=logging.INFO if os.getenv('FLASK_ENV') != 'production' else logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Flask application configuration
app = Flask(__name__)  # Create Flask application instance

# Get SECRET_KEY from environment variable or generate one (but warn in production)
secret_key = os.getenv('SECRET_KEY')
if not secret_key:
    if os.getenv('FLASK_ENV') == 'production':
        logger.error("SECRET_KEY not set in environment variables! This is required for production.")
        raise ValueError("SECRET_KEY must be set in environment variables for production")
    secret_key = os.urandom(32).hex()
    logger.warning("SECRET_KEY not set, using random key. Sessions will be invalidated on restart.")

app.config['SECRET_KEY'] = secret_key
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'uploads')  # Directory for storing uploaded files
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size limit

# Configure CORS - restrict to allowed origins in production
allowed_origins = os.getenv('ALLOWED_ORIGINS', '*')
if allowed_origins == '*':
    if os.getenv('FLASK_ENV') == 'production':
        logger.warning("CORS is set to allow all origins. This is a security risk in production!")
    cors_origins = ['*']
else:
    cors_origins = [origin.strip() for origin in allowed_origins.split(',') if origin.strip()]

CORS(app, resources={r"/api/*": {"origins": cors_origins}}, supports_credentials=True)

# Configure rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"  # In production, use Redis: "redis://localhost:6379"
)

# Ensure upload folder exists to prevent errors
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize system managers for different functionalities
data_manager = DataManager()  # Manages secure off-chain storage of encrypted files and metadata
key_manager = KeyManager()  # Handles cryptographic key management and secure key storage
user_manager = UserManager()  # User authentication and session management

# In-memory storage for file metadata (in production, use a database)
# This stores file information for quick access during web operations
file_metadata: Dict[str, Dict] = {}

# Custom Jinja2 filters
@app.template_filter('strftime')
def strftime_filter(timestamp, format_string='%Y-%m-%d %H:%M:%S'):
    """
    Custom Jinja2 filter to format Unix timestamps
    
    Args:
        timestamp: Unix timestamp (float or int)
        format_string: strftime format string (default: '%Y-%m-%d %H:%M:%S')
    
    Returns:
        Formatted date string
    """
    if timestamp is None:
        return 'Unknown'
    try:
        # Convert timestamp to local time and format
        return time.strftime(format_string, time.localtime(float(timestamp)))
    except (ValueError, TypeError, OSError):
        return 'Invalid timestamp'

# Authentication decorators
def login_required(f):
    """Decorator to require user login for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        session_token = session.get('session_token')
        if not session_token:
            flash('Please login to access this page', 'warning')
            return redirect(url_for('login'))
        
        user_info = user_manager.verify_session(session_token)
        if not user_info:
            session.pop('session_token', None)
            flash('Session expired. Please login again', 'warning')
            return redirect(url_for('login'))
        
        # Add user info to request context
        request.current_user = user_info
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to require admin role for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        session_token = session.get('session_token')
        if not session_token:
            flash('Please login to access this page', 'warning')
            return redirect(url_for('login'))
        
        user_info = user_manager.verify_session(session_token)
        if not user_info or user_info.get('role') != 'admin':
            flash('Admin access required', 'danger')
            return redirect(url_for('index'))
        
        request.current_user = user_info
        return f(*args, **kwargs)
    return decorated_function

def allowed_file(filename):
    """Check if file extension is allowed"""
    # Allow all files for demo purposes
    return True

@app.route('/')
def index():
    """Deprecated UI route; React app handles UI"""
    return jsonify({"message": "UI moved to React frontend. Use API routes under /api/.", "frontend": "http://127.0.0.1:5173"}), 410

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Deprecated UI route"""
    return jsonify({"message": "Login UI moved to frontend"}), 410

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Deprecated UI route"""
    return jsonify({"message": "Registration UI moved to frontend"}), 410

@app.route('/logout')
def logout():
    """Deprecated UI route"""
    return jsonify({"message": "Logout handled by frontend"}), 410

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    """
    File upload page - Implements the complete 7-step secure file management flow
    
    This is the core route that handles the entire secure file upload process:
    1. File Upload - User uploads file to system
    2. Off-Chain Encryption - System derives seed and encrypts file
    3. On-Chain Logging - Blockchain records access control and metadata
    
    The route handles both GET (show upload form) and POST (process upload) requests.
    """
    if request.method == 'POST':
        # Get authenticated user as owner
        current_user = request.current_user
        owner_name = current_user['username']  # Use authenticated username as owner
        
        authorized_users = request.form.get('authorized_users', '').strip()  # Comma-separated list of authorized users
        file = request.files.get('file')  # The uploaded file object
        
        if not file or file.filename == '':
            flash('Please select a file', 'danger')
            return redirect(url_for('upload'))
        
        # Process the file if it passes validation
        if file and allowed_file(file.filename):
            try:
                print(f"\n[FLOW] Starting secure file upload process...")
                
                # STEP 1: File Upload - The Uploader uploads a file to the system
                # This is the first step of our secure file management flow
                original_filename = secure_filename(file.filename)  # Sanitize filename for security
                file_id = encryption.generate_file_id(original_filename, owner_name)  # Generate unique file ID
                file_content = file.read()  # Read file content into memory
                
                # Verify file size after reading (additional check)
                max_size = 16 * 1024 * 1024  # 16MB
                if len(file_content) > max_size:
                    flash(f'File size ({len(file_content) / (1024*1024):.2f} MB) exceeds maximum limit of 16 MB', 'danger')
                    return redirect(url_for('upload'))
                
                print(f"[FLOW-1] File uploaded: {original_filename} ({len(file_content)} bytes)")
                print(f"[FLOW-1] File ID generated: {file_id}")
                
                # Parse authorized users from comma-separated string
                auth_users = [u.strip() for u in authorized_users.split(',') if u.strip()]
                
                # STEP 2: Off-Chain Encryption and Storage
                print(f"[FLOW-2] Starting off-chain encryption process...")
                
                # Create blockchain record first to get context
                file_meta = {
                    "original_filename": original_filename,
                    "size": len(file_content),
                    "upload_time": time.time(),
                    "file_hash": hashlib.sha256(file_content).hexdigest()
                }
                
                # Add block to blockchain to get block hash and timestamp
                block_hash, timestamp = blockchain.add_block(
                    file_id, owner_name, auth_users, file_meta
                )
                print(f"[FLOW-2] Blockchain context: block_hash={block_hash[:16]}..., timestamp={timestamp}")
                
                # Get or create owner secret
                owner_secret = encryption.get_or_create_owner_secret(owner_name)
                print(f"[FLOW-2] Owner secret retrieved/created for: {owner_name}")
                
                # Derive seed using blockchain context (block hash, timestamp, file ID)
                seed = encryption.derive_seed(owner_secret, block_hash, timestamp, file_id)
                print(f"[FLOW-2] Seed derived from blockchain context: {seed.hex()[:16]}...")
                
                # CHC Encryption using the derived seed
                encrypted_content = encryption.encrypt_chc(file_content, seed)
                print(f"[FLOW-2] File encrypted using CHC algorithm: {len(encrypted_content)} bytes")
                
                # Store encrypted file off-chain using data manager (now stores to Firestore)
                # The encrypted file is stored directly to Firestore - no local temporary file needed
                print(f"[FLOW-2] Storing encrypted file to Firestore cloud storage...")
                
                # Store enhanced metadata and encrypted file using data manager
                # This will upload the encrypted file to Firestore
                data_manager.store_encrypted_file(
                    file_id=file_id,
                    encrypted_data=encrypted_content,
                    original_name=original_filename,
                    block_hash=block_hash,
                    owner=owner_name,
                    authorized_users=auth_users
                )
                print(f"[FLOW-2] Encrypted file stored off-chain in Firestore: {file_id}")
                
                # STEP 3: On-Chain Logging - Log access control and metadata
                print(f"[FLOW-3] Logging access control and metadata to blockchain...")
                
                # Create access control log
                access_log = {
                    "file_id": file_id,
                    "owner": owner_name,
                    "authorized_users": auth_users,
                    "access_granted_at": timestamp,
                    "encryption_method": "CHC",
                    "block_hash": block_hash
                }
                
                # Store access control and metadata in blockchain
                blockchain.log_access_control(file_id, access_log)
                print(f"[FLOW-3] Access control logged to blockchain")
                
                # Create wrapped seeds for authorized users
                wrapped_seeds = {}
                for user in auth_users:
                    user_key = encryption.generate_user_key(user, file_id)
                    wrapped_seed = encryption.wrap_seed_for_user(seed, user_key)
                    wrapped_seeds[user] = wrapped_seed.hex()
                    # Store wrapped seed in Firestore via data_manager
                    data_manager.store_wrapped_seed(file_id, user, wrapped_seed)
                    print(f"[FLOW-3] Wrapped seed created and stored in Firestore for user: {user}")
                
                # Also wrap for owner
                owner_key = encryption.generate_user_key(owner_name, file_id)
                wrapped_seed = encryption.wrap_seed_for_user(seed, owner_key)
                wrapped_seeds[owner_name] = wrapped_seed.hex()
                # Store wrapped seed in Firestore via data_manager
                data_manager.store_wrapped_seed(file_id, owner_name, wrapped_seed)
                print(f"[FLOW-3] Wrapped seed created and stored in Firestore for owner: {owner_name}")
                
                # Store file metadata for quick access (wrapped seeds are also stored in Firestore)
                file_metadata[file_id] = {
                    "original_filename": original_filename,
                    "owner": owner_name,
                    "authorized_users": auth_users,
                    "encrypted_filename": f"{file_id}.enc",  # Reference for display
                    "wrapped_seeds": wrapped_seeds,  # Cached in memory, but also in Firestore
                    "block_hash": block_hash,
                    "timestamp": timestamp,
                    "size": len(file_content),
                    "encrypted_size": len(encrypted_content),
                    "file_hash": file_meta["file_hash"]
                }
                
                print(f"[FLOW] Upload process completed successfully!")
                print(f"[FLOW] File ID: {file_id}")
                print(f"[FLOW] Authorized users: {', '.join(auth_users) if auth_users else 'Owner only'}")
                print(f"[FLOW] Block hash: {block_hash[:32]}...")
                
                flash(f'File uploaded successfully! File ID: {file_id}', 'success')
                flash(f'Block hash: {block_hash[:32]}...', 'info')
                flash(f'Authorized users: {", ".join(auth_users) if auth_users else "Owner only"}', 'info')
                
                return redirect(url_for('files'))
                
            except Exception as e:
                print(f"[FLOW] Upload failed: {str(e)}")
                flash(f'Upload failed: {str(e)}', 'danger')
                return redirect(url_for('upload'))
    
    return jsonify({"message": "Use API route: POST /api/upload"}), 410

@app.route('/files')
@login_required
def files():
    """Deprecated UI route - delegate to API"""
    return api_files()

@app.route('/decrypt/<file_id>', methods=['GET', 'POST'])
@login_required
def decrypt(file_id):
    """Deprecated UI route - use POST /api/decrypt/<file_id>"""
    return jsonify({"message": "Use API route: POST /api/decrypt/<file_id>"}), 410

@app.route('/blockchain')
@login_required
def blockchain_view():
    """Deprecated UI route - delegate to API"""
    return api_blockchain()

@app.route('/api/blockchain')
def api_blockchain():
    """API endpoint to get blockchain data as JSON"""
    chain = blockchain.get_chain()
    return jsonify(chain)

@app.route('/api/ping')
def api_ping():
    """Health check endpoint for frontend to verify backend connectivity"""
    return jsonify({"status": "ok", "service": "flask", "ts": time.time()})

@app.route('/security/<file_id>')
@login_required
def security_audit(file_id):
    """Deprecated UI route - delegate to API"""
    return api_security_audit(file_id)

@app.route('/api/security/<file_id>')
def api_security_audit(file_id):
    """API endpoint to get security audit data as JSON"""
    # Ensure chain integrity before verification
    # This auto-repairs any issues and ensures correct verification status
    if not blockchain.verify_chain_integrity():
        print(f"[API] Chain integrity invalid, auto-repairing before security audit...")
        blockchain.repair_chain_integrity()
    
    audit_trail = blockchain.get_security_audit_trail(file_id)
    security_verification = blockchain.verify_file_security(file_id)
    
    return jsonify({
        "file_id": file_id,
        "audit_trail": audit_trail,
        "security_verification": security_verification
    })

@app.route('/api/files')
@limiter.exempt  # Exempt from rate limiting for file listing
def api_files():
    """API endpoint to list files and metadata as JSON"""
    try:
        file_blocks = blockchain.get_all_file_blocks()
        files_list = []
        
        for block in file_blocks:
            try:
                file_id = block.get('file_id')
                if not file_id or file_id == 'genesis':
                    continue
                
                if file_id in file_metadata:
                    meta = file_metadata[file_id]
                else:
                    try:
                        meta_firestore = data_manager.retrieve_file_metadata(file_id)
                        if meta_firestore:
                            meta = {
                                'original_filename': meta_firestore.get('original_name', 'Unknown'),
                                'owner': meta_firestore.get('owner', 'Unknown'),
                                'authorized_users': meta_firestore.get('authorized_users', []),
                                'block_hash': meta_firestore.get('block_hash', ''),
                                'timestamp': meta_firestore.get('storage_time', time.time()),
                                'size': block.get('data', {}).get('size', 0),
                                'encrypted_size': meta_firestore.get('size_encrypted', 0)
                            }
                            file_metadata[file_id] = meta
                        else:
                            # If metadata not found, use block data as fallback
                            block_data = block.get('data', {})
                            meta = {
                                'original_filename': block_data.get('original_filename', 'Unknown'),
                                'owner': block.get('owner', 'Unknown'),
                                'authorized_users': block.get('authorized_users', []),
                                'block_hash': block.get('block_hash', ''),
                                'timestamp': block.get('timestamp', time.time()),
                                'size': block_data.get('size', 0),
                                'encrypted_size': 0
                            }
                            file_metadata[file_id] = meta
                    except Exception as e:
                        logger.error(f"Error retrieving metadata for file {file_id}: {str(e)}")
                        # Use block data as fallback
                        block_data = block.get('data', {})
                        meta = {
                            'original_filename': block_data.get('original_filename', 'Unknown'),
                            'owner': block.get('owner', 'Unknown'),
                            'authorized_users': block.get('authorized_users', []),
                            'block_hash': block.get('block_hash', ''),
                            'timestamp': block.get('timestamp', time.time()),
                            'size': block_data.get('size', 0),
                            'encrypted_size': 0
                        }
                
                files_list.append({
                    'file_id': file_id,
                    'original_filename': meta.get('original_filename', 'Unknown'),
                    'owner': meta.get('owner', 'Unknown'),
                    'authorized_users': meta.get('authorized_users', []),
                    'block_hash': meta.get('block_hash', ''),
                    'timestamp': meta.get('timestamp'),
                    'size': meta.get('size', 0),
                    'encrypted_size': meta.get('encrypted_size', 0),
                })
            except Exception as e:
                logger.error(f"Error processing block: {str(e)}")
                continue
        
        return jsonify(files_list)
    except Exception as e:
        logger.error(f"Error in /api/files endpoint: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'error': 'Failed to retrieve files', 'message': str(e)}), 500

@app.route('/api/upload', methods=['POST'])
def api_upload():
    """API endpoint for uploading and encrypting a file (multipart/form-data)"""
    # Get username from Authorization header
    session_token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not session_token:
        return jsonify({'success': False, 'message': 'Authentication required'}), 401
    
    user_info = user_manager.verify_session(session_token)
    if not user_info:
        return jsonify({'success': False, 'message': 'Invalid or expired session'}), 401
    
    owner_name = user_info.get('username')
    
    file = request.files.get('file')
    authorized_users_str = request.form.get('authorized_users', '')
    if not file or file.filename == '':
        return jsonify({'success': False, 'message': 'No file provided'}), 400
    try:
        original_filename = secure_filename(file.filename)
        file_id = encryption.generate_file_id(original_filename, owner_name)
        file_content = file.read()
        max_size = 16 * 1024 * 1024
        if len(file_content) > max_size:
            return jsonify({'success': False, 'message': 'File exceeds 16MB limit'}), 413
        auth_users = [u.strip() for u in authorized_users_str.split(',') if u.strip()]
        file_meta = {
            "original_filename": original_filename,
            "size": len(file_content),
            "upload_time": time.time(),
            "file_hash": hashlib.sha256(file_content).hexdigest()
        }
        block_hash, timestamp = blockchain.add_block(
            file_id, owner_name, auth_users, file_meta
        )
        owner_secret = encryption.get_or_create_owner_secret(owner_name)
        seed = encryption.derive_seed(owner_secret, block_hash, timestamp, file_id)
        encrypted_content = encryption.encrypt_chc(file_content, seed)
        data_manager.store_encrypted_file(
            file_id=file_id,
            encrypted_data=encrypted_content,
            original_name=original_filename,
            block_hash=block_hash,
            owner=owner_name,
            authorized_users=auth_users
        )
        access_log = {
            "file_id": file_id,
            "owner": owner_name,
            "authorized_users": auth_users,
            "access_granted_at": timestamp,
            "encryption_method": "CHC",
            "block_hash": block_hash
        }
        blockchain.log_access_control(file_id, access_log)
        wrapped_seeds = {}
        for user in auth_users + [owner_name]:
            user_key = encryption.generate_user_key(user, file_id)
            wrapped_seed = encryption.wrap_seed_for_user(seed, user_key)
            wrapped_seeds[user] = wrapped_seed.hex()
            data_manager.store_wrapped_seed(file_id, user, wrapped_seed)
        file_metadata[file_id] = {
            "original_filename": original_filename,
            "owner": owner_name,
            "authorized_users": auth_users,
            "encrypted_filename": f"{file_id}.enc",
            "wrapped_seeds": wrapped_seeds,
            "block_hash": block_hash,
            "timestamp": timestamp,
            "size": len(file_content),
            "encrypted_size": len(encrypted_content),
            "file_hash": file_meta["file_hash"]
        }
        return jsonify({'success': True, 'file_id': file_id, 'block_hash': block_hash, 'authorized_users': auth_users})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/decrypt/<file_id>', methods=['POST'])
def api_decrypt(file_id):
    """API endpoint to decrypt and download a file for a given user"""
    # Get username from Authorization header
    session_token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not session_token:
        return jsonify({'success': False, 'message': 'Authentication required'}), 401
    
    user_info = user_manager.verify_session(session_token)
    if not user_info:
        return jsonify({'success': False, 'message': 'Invalid or expired session'}), 401
    
    user_name = user_info.get('username')
    if file_id in file_metadata:
        meta = file_metadata[file_id]
    else:
        meta_firestore = data_manager.retrieve_file_metadata(file_id)
        if not meta_firestore:
            return jsonify({'success': False, 'message': 'File not found'}), 404
        meta = {
            'original_filename': meta_firestore.get('original_name', 'Unknown'),
            'owner': meta_firestore.get('owner', 'Unknown'),
            'authorized_users': meta_firestore.get('authorized_users', []),
            'wrapped_seeds': {},
            'block_hash': meta_firestore.get('block_hash', ''),
            'timestamp': meta_firestore.get('storage_time', time.time()),
            'size': meta_firestore.get('size_encrypted', 0),
            'encrypted_size': meta_firestore.get('size_encrypted', 0)
        }
        file_metadata[file_id] = meta
    block = blockchain.get_block_by_file_id(file_id)
    if not block:
        return jsonify({'success': False, 'message': 'File metadata not found in blockchain'}), 404
    encrypted_content = data_manager.retrieve_encrypted_file(file_id)
    if not encrypted_content:
        return jsonify({'success': False, 'message': 'Encrypted file not found'}), 404
    is_authorized = (user_name == meta['owner'] or user_name in meta['authorized_users'])
    if not is_authorized:
        unauthorized_log = {
            "file_id": file_id,
            "unauthorized_user": user_name,
            "attempt_time": time.time(),
            "access_denied": True,
            "reason": "User not in authorized list"
        }
        blockchain.log_access_control(file_id, unauthorized_log)
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    wrapped_seed = data_manager.retrieve_wrapped_seed(file_id, user_name)
    if not wrapped_seed and 'wrapped_seeds' in meta and user_name in meta['wrapped_seeds']:
        wrapped_seed = bytes.fromhex(meta['wrapped_seeds'][user_name])
    if not wrapped_seed:
        return jsonify({'success': False, 'message': 'No key found for user'}), 404
    try:
        user_key = encryption.generate_user_key(user_name, file_id)
        seed = encryption.unwrap_seed_for_user(wrapped_seed, user_key)
        decrypted_content = encryption.decrypt_chc(encrypted_content, seed)
        access_log = {
            "file_id": file_id,
            "user": user_name,
            "access_time": time.time(),
            "access_granted": True,
            "decryption_successful": True
        }
        blockchain.log_access_control(file_id, access_log)
        return send_file(
            io.BytesIO(decrypted_content),
            as_attachment=True,
            download_name=meta['original_filename'],
            mimetype='application/octet-stream'
        )
    except Exception as e:
        failed_log = {
            "file_id": file_id,
            "user": user_name,
            "attempt_time": time.time(),
            "decryption_failed": True,
            "error": str(e)
        }
        blockchain.log_access_control(file_id, failed_log)
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/login', methods=['POST'])
@limiter.limit("5 per minute")  # Rate limit: 5 login attempts per minute
def api_login():
    """API endpoint for user login"""
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '')
    
    if not username or not password:
        return jsonify({'success': False, 'message': 'Username and password are required'}), 400
    
    result = user_manager.login_user(username, password)
    
    if result['success']:
        return jsonify({
            'success': True,
            'message': result['message'],
            'session_token': result['session_token'],
            'user': result['user']
        })
    else:
        return jsonify({'success': False, 'message': result['message']}), 401

@app.route('/api/register', methods=['POST'])
@limiter.limit("3 per hour")  # Rate limit: 3 registrations per hour
def api_register():
    """API endpoint for user registration"""
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '')
    email = data.get('email', '').strip()
    
    if not username or not password or not email:
        return jsonify({'success': False, 'message': 'All fields are required'}), 400
    
    if len(password) < 6:
        return jsonify({'success': False, 'message': 'Password must be at least 6 characters long'}), 400
    
    result = user_manager.register_user(username, password, email, role='user')
    
    if result['success']:
        return jsonify({
            'success': True,
            'message': result['message'],
            'user': {
                'username': result['user']['username'],
                'email': result['user']['email'],
                'role': result['user']['role']
            }
        })
    else:
        return jsonify({'success': False, 'message': result['message']}), 400

@app.route('/api/logout', methods=['POST'])
def api_logout():
    """API endpoint for user logout"""
    data = request.get_json() or {}
    session_token = data.get('session_token', '')
    
    if session_token:
        user_manager.logout_user(session_token)
    
    return jsonify({'success': True, 'message': 'Logged out successfully'})

@app.route('/api/auth/check', methods=['GET'])
def api_auth_check():
    """API endpoint to check if user is authenticated"""
    session_token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not session_token:
        return jsonify({'authenticated': False}), 401
    
    user_info = user_manager.verify_session(session_token)
    if user_info:
        return jsonify({
            'authenticated': True,
            'user': {
                'username': user_info.get('username'),
                'role': user_info.get('role')
            }
        })
    else:
        return jsonify({'authenticated': False}), 401

# Note: Authentication and profile management are future scope
# Note: Admin panel removed - simplified UI

@app.errorhandler(404)
def not_found(e):
    """404 error handler (JSON)"""
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(413)
def too_large(e):
    """File too large error handler (JSON)"""
    return jsonify({'success': False, 'message': 'File is too large. Maximum size is 16MB'}), 413

if __name__ == '__main__':
    logger.info("="*60)
    logger.info("CHC Secure File Management System")
    logger.info("="*60)
    logger.info("Initializing blockchain...")
    blockchain.init_chain()
    logger.info("Blockchain initialized")
    
    # Get configuration from environment variables
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    host = os.getenv('HOST', '127.0.0.1')
    port = int(os.getenv('PORT', 5000))
    flask_env = os.getenv('FLASK_ENV', 'development')
    
    # Warn if debug mode is enabled in production
    if debug_mode and flask_env == 'production':
        logger.error("WARNING: Debug mode is enabled in production! This is a security risk!")
    
    logger.info(f"Starting Flask server in {flask_env} mode...")
    logger.info(f"🚀 API server running at: http://{host}:{port}")
    logger.info("="*60)
    
    app.run(debug=debug_mode, host=host, port=port)
