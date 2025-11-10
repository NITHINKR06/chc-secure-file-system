import { useState, FormEvent, useEffect } from 'react'
import { Link, useParams, useNavigate } from 'react-router-dom'
import { BiLockOpen, BiFile, BiUser, BiGroup, BiChevronLeft, BiShield, BiCheckCircle } from 'react-icons/bi'
import { getCurrentUser, getAuthToken, apiGet } from '../utils/api'

export default function Decrypt() {
  const { fileId } = useParams<{ fileId: string }>()
  const [loading, setLoading] = useState(false)
  const [fileData, setFileData] = useState<any>(null)
  const [loadingFile, setLoadingFile] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    const fetchFileData = async () => {
      if (!fileId) return
      try {
        const files = await apiGet('/api/files')
        const file = Array.isArray(files) ? files.find((f: any) => f.file_id === fileId) : null
        if (file) {
          setFileData({
            filename: file.original_filename || 'Unknown',
            owner: file.owner || 'Unknown',
            authorized_users: Array.isArray(file.authorized_users) ? file.authorized_users : []
          })
        }
      } catch (err) {
        console.error('Failed to load file data:', err)
      } finally {
        setLoadingFile(false)
      }
    }
    fetchFileData()
  }, [fileId])

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    
    const user = getCurrentUser()
    if (!user) {
      alert('Please login first')
      navigate('/login')
      return
    }
    
    setLoading(true)
    try {
      const token = getAuthToken()
      const res = await fetch(`/api/decrypt/${fileId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/octet-stream',
          ...(token ? { 'Authorization': `Bearer ${token}` } : {})
        },
        credentials: 'include',
      })
      if (!res.ok) {
        const msg = await res.text().catch(() => 'Decrypt failed')
        alert(msg)
        return
      }
      const blob = await res.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      const filename = fileData?.filename || fileId || 'decrypted_file'
      a.download = filename
      document.body.appendChild(a)
      a.click()
      a.remove()
      window.URL.revokeObjectURL(url)
    } catch (err: any) {
      alert(err?.message || 'Decrypt error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      {/* Decrypt Card */}
      <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-xl p-8 border border-green-200 dark:border-green-800">
        <div className="mb-6 bg-green-600 text-white rounded-lg p-4 -mt-8 -mx-8 mb-8">
          <h2 className="text-2xl font-bold flex items-center space-x-2">
            <BiLockOpen />
            <span>Decrypt Secure File</span>
          </h2>
          <p className="text-sm text-green-100 mt-2">
            Access your encrypted file using blockchain-verified authorization
          </p>
        </div>

        {/* File Information */}
        {loadingFile ? (
          <div className="bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-700 dark:to-slate-600 rounded-xl p-6 mb-6 text-center">
            <p className="text-gray-600 dark:text-gray-400">Loading file information...</p>
          </div>
        ) : fileData ? (
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
        ) : (
          <div className="bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-700 dark:to-slate-600 rounded-xl p-6 mb-6 text-center">
            <p className="text-red-600 dark:text-red-400">File not found</p>
          </div>
        )}

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
            <span>Only authorized users can decrypt and access this secure file</span>
          </li>
          <li className="flex items-start space-x-2">
            <BiCheckCircle className="text-green-600 mt-1 flex-shrink-0" />
            <span>File decryption uses blockchain-verified access control and CHC encryption</span>
          </li>
          <li className="flex items-start space-x-2">
            <BiCheckCircle className="text-green-600 mt-1 flex-shrink-0" />
            <span>All file access and decryption attempts are logged to the blockchain audit trail</span>
          </li>
        </ul>
      </div>
    </div>
  )
}

