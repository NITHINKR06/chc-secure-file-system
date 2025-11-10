import { useState, FormEvent } from 'react'
import { Link, useParams } from 'react-router-dom'
import { BiLockOpen, BiFile, BiUser, BiGroup, BiChevronLeft, BiShield, BiCheckCircle } from 'react-icons/bi'

export default function Decrypt() {
  const { fileId } = useParams<{ fileId: string }>()
  const [loading, setLoading] = useState(false)

  // Mock data - replace with actual API call
  const fileData = {
    filename: 'document.pdf',
    owner: 'admin',
    authorized_users: ['John', 'Jane']
  }

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setLoading(true)
    // TODO: Implement decrypt logic
    setTimeout(() => setLoading(false), 3000)
  }

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      {/* Decrypt Card */}
      <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-xl p-8 border border-green-200 dark:border-green-800">
        <div className="mb-6 bg-green-600 text-white rounded-lg p-4 -mt-8 -mx-8 mb-8">
          <h2 className="text-2xl font-bold flex items-center space-x-2">
            <BiLockOpen />
            <span>Decrypt File</span>
          </h2>
        </div>

        {/* File Information */}
        <div className="bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-700 dark:to-slate-600 rounded-xl p-6 mb-6">
          <h5 className="font-bold mb-4 text-blue-600 dark:text-blue-400 flex items-center space-x-2">
            <BiFile />
            <span>File Information</span>
          </h5>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="flex items-center space-x-3">
              <BiFile className="text-2xl text-blue-600" />
              <div>
                <div className="text-sm text-gray-600 dark:text-gray-400">File Name</div>
                <div className="font-semibold text-gray-800 dark:text-white">{fileData.filename}</div>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <BiUser className="text-2xl text-blue-600" />
              <div>
                <div className="text-sm text-gray-600 dark:text-gray-400">Owner</div>
                <div className="font-semibold text-gray-800 dark:text-white">{fileData.owner}</div>
              </div>
            </div>
            <div className="flex items-center space-x-3 md:col-span-2">
              <BiGroup className="text-2xl text-blue-600" />
              <div>
                <div className="text-sm text-gray-600 dark:text-gray-400">Authorized Users</div>
                <div className="font-semibold text-gray-800 dark:text-white">
                  {fileData.authorized_users.length > 0
                    ? fileData.authorized_users.join(', ')
                    : 'Owner only'}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Decryption Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-gradient-to-r from-green-600 to-emerald-600 text-white font-semibold py-3 rounded-lg hover:from-green-700 hover:to-emerald-700 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
          >
            {loading ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                <span>Decrypting...</span>
              </>
            ) : (
              <>
                <BiLockOpen />
                <span>Decrypt & Download</span>
              </>
            )}
          </button>
          <Link
            to="/files"
            className="block w-full text-center px-6 py-3 border border-slate-300 dark:border-slate-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors flex items-center justify-center space-x-2"
          >
            <BiChevronLeft />
            <span>Back to Files</span>
          </Link>
        </form>
      </div>

      {/* Security Notice */}
      <div className="bg-green-50 dark:bg-green-900/20 rounded-xl p-6 border border-green-200 dark:border-green-800">
        <h5 className="font-bold mb-3 text-green-800 dark:text-green-300 flex items-center space-x-2">
          <BiShield />
          <span>Security Notice</span>
        </h5>
        <ul className="space-y-2 text-gray-700 dark:text-gray-300">
          <li className="flex items-start space-x-2">
            <BiCheckCircle className="text-green-600 mt-1 flex-shrink-0" />
            <span>Only authorized users can decrypt this file</span>
          </li>
          <li className="flex items-start space-x-2">
            <BiCheckCircle className="text-green-600 mt-1 flex-shrink-0" />
            <span>Decryption uses blockchain-verified access control</span>
          </li>
          <li className="flex items-start space-x-2">
            <BiCheckCircle className="text-green-600 mt-1 flex-shrink-0" />
            <span>All decryption attempts are logged to the blockchain</span>
          </li>
        </ul>
      </div>
    </div>
  )
}

