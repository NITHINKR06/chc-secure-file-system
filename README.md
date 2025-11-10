# CHC Secure File Management System

A secure file management system that implements **blockchain-linked contextual encryption** for maximum security and controlled access. This system demonstrates advanced cryptographic techniques including Contextual Hash Chain (CHC) encryption, blockchain integration, and per-user access control.

## 🎯 What This Project Is For

This project implements a **secure cloud storage system** that combines:

- **Blockchain Technology**: For immutable audit trails and contextual encryption
- **Advanced Cryptography**: CHC (Contextual Hash Chain) encryption with forward security
- **Access Control**: Per-user authorization with cryptographic key wrapping
- **Web Interface**: User-friendly Flask application for file management
- **Security Audit**: Complete audit trail for all file operations

### Key Use Cases

1. **Secure Document Storage**: Store sensitive documents with cryptographic protection
2. **Access Control Management**: Grant/revoke access to specific users
3. **Audit Compliance**: Maintain immutable records of all file operations
4. **Research & Education**: Demonstrate advanced cryptographic concepts
5. **Enterprise Security**: Foundation for secure file sharing systems

## 🏗️ System Architecture

![System Architecture Diagram](static/flowchart.png)

The system implements a **7-step secure file management flow**:

### Off-Chain Processes (Orange)
1. **File Upload** → User uploads file to system
2. **CHC Encryption** → System derives seed and encrypts file
3. **Encrypted File Storage** → Secure off-chain storage

### On-Chain Processes (Blue)
4. **Blockchain Network** → Records access control and metadata
5. **Metadata Storage** → Immutable blockchain records

### User Access Flow
6. **Authorized User Access** → Successful decryption for authorized users
7. **Unauthorized Prevention** → Access denied for unauthorized users

## 🌟 Key Features

### 🔐 Advanced Security
- **Contextual Encryption**: Each file encrypted with unique blockchain-derived seed
- **Forward Security**: CHC algorithm prevents retrospective decryption
- **Access Control**: Cryptographically enforced per-user permissions
- **Tamper-Proof Records**: Immutable blockchain audit trail

### 🛡️ Security Layers
1. **Authentication**: PBKDF2-SHA256 password hashing with secure sessions
2. **Key Management**: Master key encryption with Fernet
3. **Encryption**: CHC algorithm with HMAC chain and 256-bit seeds
4. **Blockchain**: SHA-256 hash chain for integrity
5. **Storage**: Encrypted files with checksum verification

### 📊 Admin Dashboard
- **User Management**: View, manage, and delete users
- **Storage Statistics**: Monitor usage and performance
- **Security Audit**: Complete audit trail visualization
- **Backup System**: Automated backup and recovery

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Flask
- Required Python packages (see requirements.txt)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Project
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python app.py
   ```

4. **Access the web interface**
   - Open browser: `http://127.0.0.1:5000`

## 📋 How to Use

### 1. Upload a File
- Go to **Upload** page
- Select file and enter **Owner Name**
- Specify **Authorized Users** (comma-separated)
- Click **Upload**

**What happens:**
- File encrypted using CHC algorithm
- Unique seed derived from blockchain context
- Access control logged to blockchain
- Encrypted file stored securely

### 2. View Your Files
- Go to **Files** page
- See all uploaded files with metadata
- Click **Security** to view audit trail
- Click **Decrypt** to access files

### 3. Decrypt a File
- Click **Decrypt** on any file
- Enter your **User Name**
- Click **Decrypt File**

**Access Control:**
- ✅ **Authorized users**: File decrypts successfully
- ❌ **Unauthorized users**: Access denied with audit logging

### 4. Security Audit
- Click **Security** button on any file
- View complete audit trail
- See security verification results
- Monitor access attempts and outcomes

## 🔧 Technical Implementation

### CHC Encryption Algorithm
```python
# Seed Generation
seed = HMAC-SHA256(owner_secret, block_hash + timestamp + file_id)

# CHC Encryption (per block)
for each block i:
    keystream = HMAC(state, block_index)
    ciphertext = plaintext XOR keystream
    state = HMAC(state, ciphertext)
```

### Blockchain Integration
- **Immutable Records**: SHA-256 hash chain
- **Context Generation**: Block hash + timestamp for unique seeds
- **Audit Trail**: Complete access control logging
- **Integrity Verification**: Cryptographic chain validation

### Key Management
- **Master Keys**: System and user master keys with Fernet encryption
- **Wrapped Seeds**: Per-user encrypted seeds for access control
- **Secure Storage**: Double-encrypted key vault
- **Key Derivation**: HMAC-based key generation

## 📁 Project Structure

```
Project/
├── app.py                 # Main Flask application
├── blockchain.py          # Blockchain implementation
├── encryption.py          # CHC encryption module
├── auth.py               # User authentication
├── data_manager.py       # Secure data storage
├── templates/            # HTML templates
├── static/              # CSS and static files
├── uploads/             # Encrypted file storage
├── secure_storage/      # Key vault and metadata
│   ├── encrypted_files/ # Encrypted files
│   ├── key_vault/      # Wrapped seeds
│   ├── metadata/       # File metadata
│   └── backups/        # System backups
└── test/               # Documentation and tests
```

## 🔍 Security Features

### Data Protection
- **Contextual Encryption**: Each file gets unique seed from blockchain
- **Forward Security**: CHC provides state chaining
- **Access Control**: Only authorized users can decrypt
- **Integrity Verification**: File integrity checked on access

### Audit & Monitoring
- **Complete Audit Trail**: Every action logged to blockchain
- **Security Verification**: Cryptographic verification of operations
- **Access Monitoring**: Track all access attempts
- **Tamper-Proof Records**: Immutable blockchain records

### User Management
- **Owner Control**: File owners specify authorized users
- **User Authentication**: Secure session management
- **Admin Dashboard**: System administration capabilities
- **Role-Based Access**: User and admin roles

## 📊 API Endpoints

### Core Endpoints
- `POST /upload` - Upload file with encryption
- `GET/POST /decrypt/<file_id>` - Decrypt file
- `GET /files` - List all files
- `GET /security/<file_id>` - Security audit trail
- `GET /blockchain` - View blockchain

### API Endpoints
- `GET /api/blockchain` - Blockchain data as JSON
- `GET /api/security/<file_id>` - Security audit data as JSON

## 🧪 Testing

The project includes comprehensive testing:

```bash
# Run test suite
python test/test_chc.py

# Run demo scenarios
python test/demo_secure_flow.py
```

**Test Results:**
- ✅ 14 tests passing (100% success rate)
- ✅ Cryptographic primitives verified
- ✅ CHC encryption/decryption correctness
- ✅ Access control enforcement
- ✅ Security properties validated

## 🚨 Troubleshooting

### Common Issues

**File Upload Fails**
- Check file size (max 16MB)
- Ensure valid file format
- Verify owner name provided

**Decryption Fails**
- Verify you're an authorized user
- Check if file exists in system
- Ensure correct user name

**Security Audit Empty**
- File may not have been accessed yet
- Check blockchain integrity
- Verify file metadata

## 📈 Performance Metrics

- **Encryption Speed**: ~0.0002 seconds for small files
- **Decryption Speed**: ~0.0001 seconds for small files
- **Throughput**: ~315 KB/s encryption, ~630 KB/s decryption
- **Storage Overhead**: Minimal (stream cipher efficiency)

## 🔄 Backup & Recovery

### Automatic Backups
- **Complete System Backup**: Files, keys, metadata, blockchain
- **Timestamped Backups**: Organized by date/time
- **Restore Capability**: Full system recovery
- **Integrity Verification**: Backup validation

### Manual Backup
```bash
# Create backup via admin dashboard
# Or programmatically:
python -c "from data_manager import DataManager; DataManager().create_backup()"
```

## 🌐 Web Interface

### Main Pages
- **Home** (`/`) - System overview and features
- **Upload** (`/upload`) - File upload interface
- **Files** (`/files`) - File management and listing
- **Blockchain** (`/blockchain`) - Blockchain viewer
- **Security** (`/security/<file_id>`) - Security audit trail

### Key Features
- **Real-time Feedback**: Live updates on all operations
- **Security Monitoring**: Complete audit trail visualization
- **User-friendly Interface**: Bootstrap-based responsive design
- **Mobile Support**: Works on desktop and mobile devices

## 🎯 Success Indicators

When the system is working correctly, you should see:

✅ **File Upload**: "File uploaded successfully! File ID: file_xxxxx"  
✅ **Encryption**: "File encrypted using CHC algorithm"  
✅ **Blockchain**: "Access control logged to blockchain"  
✅ **Decryption**: "File successfully decrypted"  
✅ **Security**: "Data confidentiality and integrity maintained"

## 🔧 System Requirements

- **Python**: 3.8 or higher
- **Memory**: 512MB RAM minimum
- **Storage**: 1GB free space
- **Browser**: Modern browser with JavaScript enabled
- **OS**: Windows, macOS, or Linux

## 📚 Documentation

Additional documentation available in the `test/` directory:

- `README.md` - Complete system documentation
- `IMPLEMENTATION_SUMMARY.md` - Implementation details
- `SYSTEM_ARCHITECTURE.md` - Architecture documentation
- `TECHNICAL_ARCHITECTURE.md` - Technical specifications
- `DEMO_INSTRUCTIONS.md` - Demo instructions

## 🚀 Future Enhancements

Potential improvements for production use:

1. **Real Blockchain Integration**: Ethereum, Hyperledger, or other blockchains
2. **Database Backend**: PostgreSQL, MongoDB for scalability
3. **Cloud Storage**: AWS S3, Google Cloud Storage integration
4. **Key Rotation**: Periodic key rotation for long-term security
5. **Group Access**: Hierarchical permissions and group management
6. **File Chunking**: Support for large files with chunked encryption
7. **Hardware Security**: HSM integration for key storage
8. **API Rate Limiting**: Production-ready API protection

## 📄 License

This project is for educational and research purposes. It demonstrates advanced cryptographic concepts and secure file management techniques.

## 🤝 Contributing

This is an academic project demonstrating secure file management with blockchain integration. For educational purposes and research collaboration.

---

**🎯 Ready to secure your files? Start by uploading your first file!**

The CHC Secure File Management System provides enterprise-grade security with academic-level cryptographic implementation, making it perfect for understanding advanced security concepts while maintaining practical usability.
