import { Link } from 'react-router-dom'
import { BiShield, BiKey, BiGroup, BiLock, BiUpload, BiFolder } from 'react-icons/bi'
import ArrowDown from '../components/ArrowDown'

export default function Home() {
  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <div className="text-center py-12 bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 rounded-2xl shadow-2xl text-white">
        <div className="max-w-3xl mx-auto px-4">
          <BiShield className="text-6xl mx-auto mb-4" />
          <h1 className="text-4xl md:text-5xl font-bold mb-4">
            CHC Secure Cloud Storage
          </h1>
          <p className="text-xl mb-8 text-blue-100">
            Advanced blockchain-linked contextual encryption for maximum security and controlled access
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
              Immutable blockchain records ensure data integrity and provide complete audit trails
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
              CHC algorithm with unique blockchain-derived seeds for maximum security
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
              Granular user-based authorization with cryptographic key wrapping
            </p>
          </div>

          <div className="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-lg border border-slate-200 dark:border-slate-700 hover:shadow-xl transition-shadow">
            <div className="w-16 h-16 bg-gradient-to-br from-orange-500 to-red-500 rounded-full flex items-center justify-center mb-4 mx-auto">
              <BiLock className="text-3xl text-white" />
            </div>
            <h4 className="font-bold text-lg mb-3 text-center text-gray-800 dark:text-white">
              Secure Storage
            </h4>
            <p className="text-gray-600 dark:text-gray-300 text-sm text-center">
              Encrypted files stored off-chain with tamper-proof blockchain metadata
            </p>
          </div>
        </div>
      </div>

      {/* System Flowchart */}
      <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-xl p-6 border border-slate-200 dark:border-slate-700">
        <h3 className="text-2xl font-bold mb-6 text-gray-800 dark:text-white flex items-center space-x-2">
          <BiShield />
          <span>System Flow</span>
        </h3>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* File Upload & Encryption Flow */}
          <div className="bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-700 dark:to-slate-600 rounded-xl p-6">
            <h5 className="font-bold text-lg mb-4 text-blue-600 dark:text-blue-400 flex items-center space-x-2">
              <BiUpload />
              <span>File Upload & Encryption</span>
            </h5>
            <div className="space-y-4">
              {[
                { icon: BiUpload, text: 'User Uploads File', color: 'bg-blue-500' },
                { icon: BiShield, text: 'Generate File ID', color: 'bg-cyan-500' },
                { icon: BiShield, text: 'Create Blockchain Block', subtext: '→ Get block_hash & timestamp', color: 'bg-gray-500' },
                { icon: BiKey, text: 'Derive Seed', subtext: 'from owner_secret + block_hash + timestamp + file_id', color: 'bg-purple-500' },
                { icon: BiLock, text: 'Encrypt File', subtext: 'CHC Algorithm', color: 'bg-red-500' },
                { icon: BiShield, text: 'Store Encrypted File', subtext: 'Off-Chain', color: 'bg-green-500' },
                { icon: BiGroup, text: 'Wrap Seeds for Authorized Users', color: 'bg-indigo-500' },
                { icon: BiShield, text: 'Log to Blockchain', subtext: 'Access Control', color: 'bg-gray-500' },
                { icon: BiShield, text: '✅ File Securely Stored', color: 'bg-green-600' },
              ].map((step, index) => (
                <div key={index} className="flex items-start space-x-3">
                  <div className={`${step.color} rounded-full w-10 h-10 flex items-center justify-center flex-shrink-0`}>
                    <step.icon className="text-white text-lg" />
                  </div>
                  <div className="flex-1">
                    <div className="font-semibold text-gray-800 dark:text-white">{step.text}</div>
                    {step.subtext && (
                      <div className="text-sm text-gray-600 dark:text-gray-400">{step.subtext}</div>
                    )}
                  </div>
                  {index < 8 && (
                    <div className="flex-shrink-0 pt-2">
                      <ArrowDown className="text-gray-400" />
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* File Decryption & Access Flow */}
          <div className="bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-700 dark:to-slate-600 rounded-xl p-6">
            <h5 className="font-bold text-lg mb-4 text-green-600 dark:text-green-400 flex items-center space-x-2">
              <BiLock />
              <span>File Decryption & Access</span>
            </h5>
            <div className="space-y-4">
              {[
                { icon: BiUpload, text: 'User Requests Decryption', color: 'bg-blue-500' },
                { icon: BiShield, text: 'Retrieve Metadata', subtext: 'Blockchain', color: 'bg-gray-500' },
                { icon: BiShield, text: 'Retrieve Encrypted File', subtext: 'Off-Chain', color: 'bg-green-500' },
                { icon: BiShield, text: 'Check Authorization', color: 'bg-indigo-500' },
                { 
                  icon: BiShield, 
                  text: 'If Authorized:', 
                  subtext: '• Unwrap Seed\n• Decrypt File\n• Log Success',
                  color: 'bg-yellow-500' 
                },
                { icon: BiShield, text: '✅ File Decrypted', color: 'bg-green-600' },
              ].map((step, index) => (
                <div key={index} className="flex items-start space-x-3">
                  <div className={`${step.color} rounded-full w-10 h-10 flex items-center justify-center flex-shrink-0`}>
                    <step.icon className="text-white text-lg" />
                  </div>
                  <div className="flex-1">
                    <div className="font-semibold text-gray-800 dark:text-white">{step.text}</div>
                    {step.subtext && (
                      <div className="text-sm text-gray-600 dark:text-gray-400 whitespace-pre-line">{step.subtext}</div>
                    )}
                  </div>
                  {index < 5 && (
                    <div className="flex-shrink-0 pt-2">
                      <ArrowDown className="text-gray-400" />
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

