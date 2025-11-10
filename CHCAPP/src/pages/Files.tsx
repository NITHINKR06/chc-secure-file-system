import { useState } from 'react'
import { Link } from 'react-router-dom'
import { BiLock, BiPlusCircle, BiFile, BiKey, BiUser, BiGroup, BiHdd, BiCalendar, BiLockOpen, BiShield, BiNetworkChart } from 'react-icons/bi'

// Mock data - replace with actual API calls
const mockFiles = [
  {
    file_id: 'file123',
    original_filename: 'document.pdf',
    owner: 'admin',
    authorized_users: 'John, Jane',
    size: '2.5 MB',
    encrypted_size: '2.5 MB',
    timestamp: '2024-01-15 10:30:00'
  },
  {
    file_id: 'file456',
    original_filename: 'image.jpg',
    owner: 'user1',
    authorized_users: 'Owner only',
    size: '1.2 MB',
    encrypted_size: '1.2 MB',
    timestamp: '2024-01-14 15:45:00'
  }
]

export default function Files() {
  const [files] = useState(mockFiles)

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-800 dark:text-white flex items-center space-x-2">
          <BiLock className="text-blue-600" />
          <span>Encrypted Files</span>
        </h2>
        <Link
          to="/upload"
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-2"
        >
          <BiPlusCircle />
          <span>Upload New File</span>
        </Link>
      </div>

      {/* Files Table */}
      {files.length > 0 ? (
        <>
          <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-slate-100 dark:bg-slate-700">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 dark:text-gray-300 uppercase tracking-wider">
                      <BiFile className="inline mr-1" />
                      File Name
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 dark:text-gray-300 uppercase tracking-wider">
                      <BiKey className="inline mr-1" />
                      File ID
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 dark:text-gray-300 uppercase tracking-wider">
                      <BiUser className="inline mr-1" />
                      Owner
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 dark:text-gray-300 uppercase tracking-wider">
                      <BiGroup className="inline mr-1" />
                      Authorized Users
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 dark:text-gray-300 uppercase tracking-wider">
                      <BiHdd className="inline mr-1" />
                      Size
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 dark:text-gray-300 uppercase tracking-wider">
                      <BiCalendar className="inline mr-1" />
                      Upload Time
                    </th>
                    <th className="px-6 py-3 text-center text-xs font-medium text-gray-700 dark:text-gray-300 uppercase tracking-wider">
                      <BiFile className="inline mr-1" />
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white dark:bg-slate-800 divide-y divide-slate-200 dark:divide-slate-700">
                  {files.map((file, index) => (
                    <tr key={file.file_id} className="hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center space-x-3">
                          <BiFile className="text-2xl text-blue-600" />
                          <div>
                            <div className="font-semibold text-gray-900 dark:text-white">
                              {file.original_filename}
                            </div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <code className="text-red-600 dark:text-red-400 font-bold text-sm">
                          {file.file_id}
                        </code>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="px-2 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded text-sm font-medium">
                          <BiUser className="inline mr-1" />
                          {file.owner}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {file.authorized_users === 'Owner only' ? (
                          <span className="px-2 py-1 bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200 rounded text-sm">
                            <BiLock className="inline mr-1" />
                            Owner only
                          </span>
                        ) : (
                          <span className="px-2 py-1 bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 rounded text-sm">
                            <BiGroup className="inline mr-1" />
                            {file.authorized_users}
                          </span>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600 dark:text-gray-400">
                        <div>
                          <BiFile className="inline mr-1" />
                          {file.size}
                        </div>
                        <div>
                          <BiLock className="inline mr-1" />
                          {file.encrypted_size}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600 dark:text-gray-400">
                        <BiCalendar className="inline mr-1" />
                        {file.timestamp}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-center">
                        <div className="flex justify-center space-x-2">
                          <Link
                            to={`/decrypt/${file.file_id}`}
                            className="px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors text-sm flex items-center space-x-1"
                          >
                            <BiLockOpen />
                            <span>Decrypt</span>
                          </Link>
                          <Link
                            to={`/security/${file.file_id}`}
                            className="px-3 py-1 bg-cyan-600 text-white rounded hover:bg-cyan-700 transition-colors text-sm flex items-center space-x-1"
                          >
                            <BiShield />
                            <span>Security</span>
                          </Link>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Statistics Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white dark:bg-slate-800 rounded-xl shadow-lg p-6 border border-slate-200 dark:border-slate-700 text-center">
              <div className="w-16 h-16 bg-blue-100 dark:bg-blue-900 rounded-full flex items-center justify-center mx-auto mb-4">
                <BiFile className="text-3xl text-blue-600 dark:text-blue-400" />
              </div>
              <h3 className="text-3xl font-bold text-blue-600 mb-1">{files.length}</h3>
              <p className="text-gray-600 dark:text-gray-400">Total Files</p>
            </div>
            <div className="bg-white dark:bg-slate-800 rounded-xl shadow-lg p-6 border border-slate-200 dark:border-slate-700 text-center">
              <div className="w-16 h-16 bg-green-100 dark:bg-green-900 rounded-full flex items-center justify-center mx-auto mb-4">
                <BiShield className="text-3xl text-green-600 dark:text-green-400" />
              </div>
              <h3 className="text-3xl font-bold text-green-600 mb-1">{files.length}</h3>
              <p className="text-gray-600 dark:text-gray-400">Encrypted Files</p>
            </div>
            <div className="bg-white dark:bg-slate-800 rounded-xl shadow-lg p-6 border border-slate-200 dark:border-slate-700 text-center">
              <div className="w-16 h-16 bg-purple-100 dark:bg-purple-900 rounded-full flex items-center justify-center mx-auto mb-4">
                <BiNetworkChart className="text-3xl text-purple-600 dark:text-purple-400" />
              </div>
              <h3 className="text-3xl font-bold text-purple-600 mb-1">{files.length}</h3>
              <p className="text-gray-600 dark:text-gray-400">Blockchain Records</p>
            </div>
          </div>
        </>
      ) : (
        <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-xl p-12 border border-slate-200 dark:border-slate-700 text-center">
          <BiFile className="text-6xl mx-auto mb-4 text-gray-400" />
          <h4 className="text-xl font-semibold text-gray-600 dark:text-gray-400 mb-3">
            No Files Uploaded Yet
          </h4>
          <p className="text-gray-500 dark:text-gray-500 mb-6">Upload your first file to see it here</p>
          <Link
            to="/upload"
            className="inline-flex items-center space-x-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <BiFile />
            <span>Upload First File</span>
          </Link>
        </div>
      )}
    </div>
  )
}

