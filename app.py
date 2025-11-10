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

# Import custom modules for system functionality
from data_manager import DataManager, KeyManager  # Secure data storage and key management
from auth import UserManager  # User authentication and management

# Flask application configuration
app = Flask(__name__)  # Create Flask application instance
app.config['SECRET_KEY'] = os.urandom(32).hex()  # Generate random secret key for flash messages
app.config['UPLOAD_FOLDER'] = 'uploads'  # Directory for storing uploaded files
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size limit

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
    """Home page with introduction"""
    # Get current user if logged in
    current_user = None
    session_token = session.get('session_token')
    if session_token:
        current_user = user_manager.verify_session(session_token)
    
    return render_template('index.html', current_user=current_user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login page"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            flash('Username and password are required', 'danger')
            return redirect(url_for('login'))
        
        result = user_manager.login_user(username, password)
        
        if result['success']:
            session['session_token'] = result['session_token']
            session['username'] = result['user']['username']
            flash(f"Welcome back, {result['user']['username']}!", 'success')
            next_page = request.args.get('next') or url_for('index')
            return redirect(next_page)
        else:
            flash(result['message'], 'danger')
            return redirect(url_for('login'))
    
    # If already logged in, redirect to home
    session_token = session.get('session_token')
    if session_token and user_manager.verify_session(session_token):
        return redirect(url_for('index'))
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration page"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        email = request.form.get('email', '').strip()
        
        if not username or not password or not email:
            flash('All fields are required', 'danger')
            return redirect(url_for('register'))
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long', 'danger')
            return redirect(url_for('register'))
        
        result = user_manager.register_user(username, password, email, role='user')
        
        if result['success']:
            flash('Registration successful! Please login', 'success')
            return redirect(url_for('login'))
        else:
            flash(result['message'], 'danger')
            return redirect(url_for('register'))
    
    # If already logged in, redirect to home
    session_token = session.get('session_token')
    if session_token and user_manager.verify_session(session_token):
        return redirect(url_for('index'))
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    """User logout"""
    session_token = session.get('session_token')
    if session_token:
        user_manager.logout_user(session_token)
        session.pop('session_token', None)
        session.pop('username', None)
        flash('You have been logged out successfully', 'info')
    return redirect(url_for('index'))

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
    
    return render_template('upload.html')

@app.route('/files')
@login_required
def files():
    """List all uploaded files"""
    # Get all file blocks from blockchain
    file_blocks = blockchain.get_all_file_blocks()
    
    # Combine with metadata (from memory or Firestore)
    files_list = []
    for block in file_blocks:
        file_id = block.get('file_id')
        
        # Try to get metadata from in-memory cache first
        if file_id in file_metadata:
            meta = file_metadata[file_id]
        else:
            # Load from Firestore if not in memory
            meta_firestore = data_manager.retrieve_file_metadata(file_id)
            if meta_firestore:
                # Convert Firestore metadata to expected format
                meta = {
                    'original_filename': meta_firestore.get('original_name', 'Unknown'),
                    'owner': meta_firestore.get('owner', 'Unknown'),
                    'authorized_users': meta_firestore.get('authorized_users', []),
                    'block_hash': meta_firestore.get('block_hash', ''),
                    'timestamp': meta_firestore.get('storage_time', time.time()),
                    'size': block.get('data', {}).get('size', 0),
                    'encrypted_size': meta_firestore.get('size_encrypted', 0)
                }
                # Cache in memory for future use
                file_metadata[file_id] = meta
            else:
                # Skip if metadata not found
                continue
        
        files_list.append({
            'file_id': file_id,
            'original_filename': meta['original_filename'],
            'owner': meta['owner'],
            'authorized_users': ', '.join(meta['authorized_users']) if meta['authorized_users'] else 'Owner only',
            'block_hash': meta['block_hash'][:32] + '...' if meta['block_hash'] else 'N/A',
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(meta['timestamp'])),
            'size': f"{meta['size']:,} bytes",
            'encrypted_size': f"{meta['encrypted_size']:,} bytes"
        })
    
    return render_template('files.html', files=files_list)

@app.route('/decrypt/<file_id>', methods=['GET', 'POST'])
@login_required
def decrypt(file_id):
    """Decrypt a file - Implements the file access and retrieval flow"""
    # Check if file exists (in memory or Firestore)
    if file_id in file_metadata:
        meta = file_metadata[file_id]
    else:
        # Load from Firestore if not in memory
        meta_firestore = data_manager.retrieve_file_metadata(file_id)
        if not meta_firestore:
            flash('File not found', 'danger')
            return redirect(url_for('files'))
        
        # Convert Firestore metadata to expected format
        meta = {
            'original_filename': meta_firestore.get('original_name', 'Unknown'),
            'owner': meta_firestore.get('owner', 'Unknown'),
            'authorized_users': meta_firestore.get('authorized_users', []),
            'wrapped_seeds': {},  # Will be loaded from Firestore when needed
            'block_hash': meta_firestore.get('block_hash', ''),
            'timestamp': meta_firestore.get('storage_time', time.time()),
            'size': meta_firestore.get('size_encrypted', 0),
            'encrypted_size': meta_firestore.get('size_encrypted', 0)
        }
        # Cache in memory for future use
        file_metadata[file_id] = meta
    
    if request.method == 'POST':
        # Get authenticated user
        current_user = request.current_user
        user_name = current_user['username']  # Use authenticated username
        
        print(f"\n[FLOW] Starting file access and retrieval process...")
        print(f"[FLOW] User: {user_name}, File: {file_id}")
        
        # STEP 4: File Access and Retrieval
        print(f"[FLOW-4] Retrieving metadata and ciphertext...")
        
        # Retrieve metadata from blockchain
        block = blockchain.get_block_by_file_id(file_id)
        if not block:
            flash('File metadata not found in blockchain', 'danger')
            return redirect(url_for('files'))
        
        print(f"[FLOW-4] Metadata retrieved from blockchain: block_hash={block.get('block_hash', '')[:16]}...")
        
        # Retrieve ciphertext from off-chain storage using data manager
        encrypted_content = data_manager.retrieve_encrypted_file(file_id)
        if not encrypted_content:
            flash('Encrypted file not found or corrupted', 'danger')
            return redirect(url_for('files'))
        
        print(f"[FLOW-4] Ciphertext retrieved from off-chain storage: {len(encrypted_content)} bytes")
        
        # Verify file integrity
        if not data_manager.verify_file_integrity(file_id):
            flash('File integrity check failed', 'danger')
            return redirect(url_for('files'))
        
        print(f"[FLOW-4] File integrity verified")
        
        # Check if user is authorized
        is_authorized = (user_name == meta['owner'] or 
                        user_name in meta['authorized_users'])
        
        if not is_authorized:
            # STEP 6: Unauthorized User Access
            print(f"[FLOW-6] Unauthorized access attempt by {user_name} for file {file_id}")
            print(f"[FLOW-6] User {user_name} is not in authorized list: {meta['authorized_users']}")
            print(f"[FLOW-6] Owner: {meta['owner']}")
            
            # Log unauthorized access attempt
            unauthorized_log = {
                "file_id": file_id,
                "unauthorized_user": user_name,
                "attempt_time": time.time(),
                "access_denied": True,
                "reason": "User not in authorized list"
            }
            blockchain.log_access_control(file_id, unauthorized_log)
            
            flash('Access Denied: You are not authorized to decrypt this file', 'danger')
            return redirect(url_for('decrypt', file_id=file_id))
        
        # STEP 5: Authorized User Access
        print(f"[FLOW-5] Authorized user access granted for {user_name}")
        
        try:
            # Get wrapped seed for user (from in-memory metadata or Firestore)
            wrapped_seed = None
            if user_name in meta.get('wrapped_seeds', {}):
                # Get from in-memory metadata
                wrapped_seed_hex = meta['wrapped_seeds'][user_name]
                wrapped_seed = bytes.fromhex(wrapped_seed_hex)
                print(f"[FLOW-5] Retrieved wrapped seed from in-memory metadata for user: {user_name}")
            else:
                # Try to retrieve from Firestore via data_manager
                wrapped_seed = data_manager.retrieve_wrapped_seed(file_id, user_name)
                if wrapped_seed:
                    print(f"[FLOW-5] Retrieved wrapped seed from Firestore for user: {user_name}")
                else:
                    flash('No encryption key found for your user', 'danger')
                    return redirect(url_for('decrypt', file_id=file_id))
            
            # Generate user key and unwrap seed (Key Derivation & Decryption)
            user_key = encryption.generate_user_key(user_name, file_id)
            seed = encryption.unwrap_seed_for_user(wrapped_seed, user_key)
            
            print(f"[FLOW-5] Key derivation successful for user {user_name}")
            print(f"[FLOW-5] Seed unwrapped: {seed.hex()[:16]}...")
            
            # Decrypt file using the derived seed
            decrypted_content = encryption.decrypt_chc(encrypted_content, seed)
            
            print(f"[FLOW-5] File successfully decrypted: {len(decrypted_content)} bytes")
            
            # Log successful access
            access_log = {
                "file_id": file_id,
                "user": user_name,
                "access_time": time.time(),
                "access_granted": True,
                "decryption_successful": True
            }
            blockchain.log_access_control(file_id, access_log)
            
            # STEP 7: Security Outcome - Data confidentiality and integrity maintained
            print(f"[FLOW-7] Security outcome: Data successfully decrypted for authorized user")
            print(f"[FLOW-7] File access cryptographically verified via blockchain")
            
            # Return decrypted file
            return send_file(
                io.BytesIO(decrypted_content),
                as_attachment=True,
                download_name=meta['original_filename'],
                mimetype='application/octet-stream'
            )
            
        except Exception as e:
            print(f"[FLOW-5] Decryption failed: {str(e)}")
            
            # Log failed decryption attempt
            failed_log = {
                "file_id": file_id,
                "user": user_name,
                "attempt_time": time.time(),
                "decryption_failed": True,
                "error": str(e)
            }
            blockchain.log_access_control(file_id, failed_log)
            
            flash(f'Decryption failed: {str(e)}', 'danger')
            return redirect(url_for('decrypt', file_id=file_id))
    
    # GET request - show decrypt form
    current_user = request.current_user
    return render_template('decrypt.html', 
                         file_id=file_id,
                         filename=meta['original_filename'],
                         owner=meta['owner'],
                         authorized_users=meta['authorized_users'],
                         current_user=current_user)

@app.route('/blockchain')
@login_required
def blockchain_view():
    """View blockchain ledger"""
    chain = blockchain.get_chain()
    
    # Format blocks for display
    formatted_chain = []
    for block in chain:
        formatted_chain.append(blockchain.format_block_for_display(block))
    
    # Verify chain integrity
    is_valid = blockchain.verify_chain_integrity()
    
    return render_template('blockchain.html', 
                         chain=formatted_chain,
                         chain_length=len(chain),
                         is_valid=is_valid)

@app.route('/api/blockchain')
def api_blockchain():
    """API endpoint to get blockchain data as JSON"""
    chain = blockchain.get_chain()
    return jsonify(chain)

@app.route('/security/<file_id>')
@login_required
def security_audit(file_id):
    """View security audit trail for a file"""
    # Check if file exists (in memory or Firestore)
    if file_id in file_metadata:
        meta = file_metadata[file_id]
    else:
        # Load from Firestore if not in memory
        meta_firestore = data_manager.retrieve_file_metadata(file_id)
        if not meta_firestore:
            flash('File not found', 'danger')
            return redirect(url_for('files'))
        
        # Convert Firestore metadata to expected format
        meta = {
            'original_filename': meta_firestore.get('original_name', 'Unknown'),
            'owner': meta_firestore.get('owner', 'Unknown'),
            'authorized_users': meta_firestore.get('authorized_users', []),
            'block_hash': meta_firestore.get('block_hash', ''),
            'timestamp': meta_firestore.get('storage_time', time.time())
        }
        # Cache in memory for future use
        file_metadata[file_id] = meta
    
    # Get security audit trail
    audit_trail = blockchain.get_security_audit_trail(file_id)
    
    # Get security verification
    security_verification = blockchain.verify_file_security(file_id)
    
    return render_template('security_audit.html',
                         file_id=file_id,
                         filename=meta['original_filename'],
                         owner=meta['owner'],
                         authorized_users=meta['authorized_users'],
                         audit_trail=audit_trail,
                         security_verification=security_verification)

@app.route('/api/security/<file_id>')
def api_security_audit(file_id):
    """API endpoint to get security audit data as JSON"""
    audit_trail = blockchain.get_security_audit_trail(file_id)
    security_verification = blockchain.verify_file_security(file_id)
    
    return jsonify({
        "file_id": file_id,
        "audit_trail": audit_trail,
        "security_verification": security_verification
    })

# Note: Authentication and profile management are future scope
# Note: Admin panel removed - simplified UI

@app.errorhandler(404)
def not_found(e):
    """404 error handler"""
    return render_template('index.html'), 404

@app.errorhandler(413)
def too_large(e):
    """File too large error handler"""
    flash('File is too large. Maximum size is 16MB', 'danger')
    return redirect(url_for('upload'))

if __name__ == '__main__':
    print("\n" + "="*60)
    print("CHC - Contextual Encryption for Secure Cloud Storage")
    print("="*60)
    print("\nInitializing blockchain...")
    blockchain.init_chain()
    print("\nStarting Flask server...")
    print("\n🚀 Application running at: http://127.0.0.1:5000")
    print("="*60 + "\n")
    
    app.run(debug=True, host='127.0.0.1', port=5000)
