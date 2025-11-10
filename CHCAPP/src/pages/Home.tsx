import { Link } from 'react-router-dom'
import { BiShield, BiKey, BiGroup, BiLock, BiUpload, BiFolder } from 'react-icons/bi'

export default function Home() {
  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <div className="text-center py-12 bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 rounded-2xl shadow-2xl text-white">
        <div className="max-w-3xl mx-auto px-4">
          <BiShield className="text-6xl mx-auto mb-4" />
          <h1 className="text-4xl md:text-5xl font-bold mb-4">
            CHC Secure File Management System
          </h1>
          <p className="text-xl mb-8 text-blue-100">
            Enterprise-grade secure file storage with blockchain-linked contextual encryption for maximum security and controlled file access
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              to="/upload"
              className="px-6 py-3 bg-white text-blue-600 font-semibold rounded-lg hover:bg-blue-50 transition-colors flex items-center justify-center space-x-2"
            >
              <BiUpload />
              <span>Upload File</span>
            </Link>
            <Link
              to="/files"
              className="px-6 py-3 bg-blue-500 text-white font-semibold rounded-lg hover:bg-blue-400 transition-colors flex items-center justify-center space-x-2 border border-white"
            >
              <BiFolder />
              <span>View Files</span>
            </Link>
          </div>
        </div>
      </div>

      {/* Features Grid */}
      <div>
        <h2 className="text-3xl font-bold text-center mb-8 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
          Key Features
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-lg border border-slate-200 dark:border-slate-700 hover:shadow-xl transition-shadow">
            <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-blue-600 rounded-full flex items-center justify-center mb-4 mx-auto">
              <BiShield className="text-3xl text-white" />
            </div>
            <h4 className="font-bold text-lg mb-3 text-center text-gray-800 dark:text-white">
              Blockchain Security
            </h4>
            <p className="text-gray-600 dark:text-gray-300 text-sm text-center">
              Immutable blockchain records ensure file integrity and provide complete audit trails for all file operations
            </p>
          </div>

          <div className="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-lg border border-slate-200 dark:border-slate-700 hover:shadow-xl transition-shadow">
            <div className="w-16 h-16 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full flex items-center justify-center mb-4 mx-auto">
              <BiKey className="text-3xl text-white" />
            </div>
            <h4 className="font-bold text-lg mb-3 text-center text-gray-800 dark:text-white">
              Contextual Encryption
            </h4>
            <p className="text-gray-600 dark:text-gray-300 text-sm text-center">
              CHC algorithm encrypts each file with unique blockchain-derived seeds for maximum file security
            </p>
          </div>

          <div className="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-lg border border-slate-200 dark:border-slate-700 hover:shadow-xl transition-shadow">
            <div className="w-16 h-16 bg-gradient-to-br from-green-500 to-emerald-500 rounded-full flex items-center justify-center mb-4 mx-auto">
              <BiGroup className="text-3xl text-white" />
            </div>
            <h4 className="font-bold text-lg mb-3 text-center text-gray-800 dark:text-white">
              Access Control
            </h4>
            <p className="text-gray-600 dark:text-gray-300 text-sm text-center">
              Granular file access control with per-user authorization and cryptographic key wrapping
            </p>
          </div>

          <div className="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-lg border border-slate-200 dark:border-slate-700 hover:shadow-xl transition-shadow">
            <div className="w-16 h-16 bg-gradient-to-br from-orange-500 to-red-500 rounded-full flex items-center justify-center mb-4 mx-auto">
              <BiLock className="text-3xl text-white" />
            </div>
            <h4 className="font-bold text-lg mb-3 text-center text-gray-800 dark:text-white">
              Secure File Storage
            </h4>
            <p className="text-gray-600 dark:text-gray-300 text-sm text-center">
              Encrypted files stored securely with tamper-proof blockchain metadata and integrity verification
            </p>
          </div>
        </div>
      </div>

      {/* System Flowchart */}
      <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-xl p-6 border border-slate-200 dark:border-slate-700">
        <h3 className="text-2xl font-bold mb-4 text-gray-800 dark:text-white flex items-center space-x-2">
          <BiShield />
          <span>Secure File Management System Flow</span>
        </h3>
        <p className="text-sm text-gray-600 dark:text-gray-400 mb-6">
          How files are securely managed with CHC encryption and blockchain protection
        </p>
        
        <div className="flex justify-center items-center">
          <img 
            src="/flowchart.png" 
            alt="Secure File Management System Flow Diagram showing File Upload & Encryption and File Decryption & Access processes" 
            className="max-w-full h-auto rounded-lg shadow-lg"
          />
        </div>
      </div>
    </div>
  )
}

