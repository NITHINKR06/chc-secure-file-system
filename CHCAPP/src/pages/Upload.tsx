import { useState, FormEvent, DragEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { BiCloudUpload, BiFile, BiGroup, BiLock, BiChevronLeft, BiInfoCircle, BiCheckCircle } from 'react-icons/bi'
import { getCurrentUser, getAuthToken } from '../utils/api'

export default function Upload() {
  const navigate = useNavigate()
  const [file, setFile] = useState<File | null>(null)
  const [authorizedUsers, setAuthorizedUsers] = useState('')
  const [loading, setLoading] = useState(false)
  const [dragActive, setDragActive] = useState(false)

  const handleDrag = (e: DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const handleDrop = (e: DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelect(e.dataTransfer.files[0])
    }
  }

  const handleFileSelect = (selectedFile: File) => {
    const maxSize = 16 * 1024 * 1024 // 16MB
    if (selectedFile.size > maxSize) {
      alert('File size exceeds 16MB limit. Please choose a smaller file.')
      return
    }
    setFile(selectedFile)
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i]
  }

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    if (!file) return
    
    const user = getCurrentUser()
    if (!user) {
      alert('Please login first')
      navigate('/login')
      return
    }
    
    setLoading(true)
    try {
      const token = getAuthToken()
      const form = new FormData()
      form.append('file', file)
      form.append('authorized_users', authorizedUsers)
      const res = await fetch('/api/upload', {
        method: 'POST',
        headers: token ? { 'Authorization': `Bearer ${token}` } : {},
        body: form,
        credentials: 'include',
      })
      if (!res.ok) {
        const msg = await res.text().catch(() => 'Upload failed')
        alert(msg)
      } else {
        const data = await res.json()
        if (data?.success) {
          alert(`Uploaded! File ID: ${data.file_id}`)
          setFile(null)
          setAuthorizedUsers('')
          navigate('/files')
        } else {
          alert(data?.message || 'Upload failed')
        }
      }
    } catch (err: any) {
      alert(err?.message || 'Upload error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      {/* Upload Card */}
      <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-xl p-8 border border-slate-200 dark:border-slate-700">
        <div className="mb-6">
          <h2 className="text-2xl font-bold text-gray-800 dark:text-white flex items-center space-x-2">
            <BiCloudUpload className="text-blue-600" />
            <span>Upload & Secure File</span>
          </h2>
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-2">
            Upload your file to the secure file management system with CHC encryption and blockchain protection
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* File Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              <BiFile className="inline mr-2 text-blue-600" />
              Select File <span className="text-red-500">*</span>
            </label>
            <div
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
              onClick={() => document.getElementById('file-input')?.click()}
              className={`border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition-colors ${
                dragActive
                  ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                  : 'border-slate-300 dark:border-slate-600 hover:border-blue-400 dark:hover:border-blue-500'
              }`}
            >
              <input
                type="file"
                id="file-input"
                className="hidden"
                onChange={(e) => {
                  if (e.target.files && e.target.files[0]) {
                    handleFileSelect(e.target.files[0])
                  }
                }}
                required
              />
              <BiCloudUpload className="text-5xl mx-auto mb-4 text-blue-600" />
              <h5 className="text-lg font-semibold mb-2 text-gray-800 dark:text-white">
                Drag & Drop your file here
              </h5>
              <p className="text-gray-600 dark:text-gray-400 mb-4">or click to browse</p>
              <button
                type="button"
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                Choose File
              </button>
              {file && (
                <div className="mt-4 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                  <div className="flex items-center justify-center space-x-2 text-blue-700 dark:text-blue-300">
                    <BiFile />
                    <span className="font-semibold">{file.name}</span>
                    <span className="text-sm text-gray-600 dark:text-gray-400">
                      ({formatFileSize(file.size)})
                    </span>
                  </div>
                </div>
              )}
            </div>
            <p className="mt-2 text-sm text-gray-500 dark:text-gray-400 flex items-center space-x-1">
              <BiFile />
              <span>Maximum file size: 16 MB</span>
            </p>
          </div>

          {/* Authorized Users */}
          <div>
            <label htmlFor="authorized_users" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              <BiGroup className="inline mr-2 text-blue-600" />
              Authorized Users <span className="text-gray-500">(Optional)</span>
            </label>
            <input
              type="text"
              id="authorized_users"
              value={authorizedUsers}
              onChange={(e) => setAuthorizedUsers(e.target.value)}
              className="w-full px-4 py-3 border border-slate-300 dark:border-slate-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-slate-700 dark:text-white"
              placeholder="Enter names separated by commas (e.g., John, Jane, Bob)"
            />
            <p className="mt-2 text-sm text-gray-500 dark:text-gray-400 flex items-center space-x-1">
              <BiGroup />
              <span>Users who can decrypt this file (comma-separated)</span>
            </p>
          </div>

          {/* Submit Buttons */}
          <div className="space-y-3">
            <button
              type="submit"
              disabled={loading || !file}
              className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-semibold py-3 rounded-lg hover:from-blue-700 hover:to-indigo-700 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                  <span>Encrypting & Uploading...</span>
                </>
              ) : (
                <>
                  <BiLock />
                  <span>Encrypt & Upload</span>
                </>
              )}
            </button>
            <Link
              to="/"
              className="block w-full text-center px-6 py-3 border border-slate-300 dark:border-slate-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors flex items-center justify-center space-x-2"
            >
              <BiChevronLeft />
              <span>Back to Home</span>
            </Link>
          </div>
        </form>
      </div>

      {/* Info Card */}
      <div className="bg-yellow-50 dark:bg-yellow-900/20 rounded-xl p-6 border border-yellow-200 dark:border-yellow-800">
        <h5 className="font-bold mb-3 text-yellow-800 dark:text-yellow-300 flex items-center space-x-2">
          <BiInfoCircle />
          <span>What happens next?</span>
        </h5>
        <ul className="space-y-2 text-gray-700 dark:text-gray-300">
          <li className="flex items-start space-x-2">
            <BiCheckCircle className="text-green-600 mt-1 flex-shrink-0" />
            <span>Your file will be encrypted using the CHC (Contextual Hash Chain) algorithm</span>
          </li>
          <li className="flex items-start space-x-2">
            <BiCheckCircle className="text-green-600 mt-1 flex-shrink-0" />
            <span>A unique encryption seed will be derived from blockchain context</span>
          </li>
          <li className="flex items-start space-x-2">
            <BiCheckCircle className="text-green-600 mt-1 flex-shrink-0" />
            <span>Encrypted file will be stored securely in the file management system</span>
          </li>
          <li className="flex items-start space-x-2">
            <BiCheckCircle className="text-green-600 mt-1 flex-shrink-0" />
            <span>File access control and metadata will be logged to the blockchain</span>
          </li>
        </ul>
      </div>
    </div>
  )
}

