import { Link, useParams } from 'react-router-dom'
import { BiShield, BiFile, BiUser, BiGroup, BiChevronLeft, BiLockOpen, BiListUl, BiCloudUpload, BiCheckCircle, BiXCircle, BiErrorAlt } from 'react-icons/bi'

export default function SecurityAudit() {
  const { fileId } = useParams<{ fileId: string }>()

  // Mock data - replace with actual API call
  const auditData = {
    file_id: fileId || 'file123',
    filename: 'document.pdf',
    owner: 'admin',
    authorized_users: ['John', 'Jane'],
    security_verification: {
      data_confidentiality: 'maintained',
      access_control: 'enforced',
      cryptographic_verification: 'verified',
      security_events: {
        successful_accesses: 5,
        unauthorized_attempts: 2,
        failed_decryptions: 1
      }
    },
    audit_trail: [
      {
        event: 'file_uploaded',
        description: 'File uploaded and encrypted',
        timestamp: '2024-01-15 10:30:00',
        user: 'admin'
      },
      {
        event: 'authorized_access',
        description: 'File successfully decrypted',
        timestamp: '2024-01-15 11:00:00',
        user: 'John'
      },
      {
        event: 'unauthorized_access_attempt',
        description: 'Unauthorized user attempted to access file',
        timestamp: '2024-01-15 12:00:00',
        user: 'unauthorized_user',
        reason: 'User not in authorized list'
      }
    ]
  }

  const getEventIcon = (event: string) => {
    switch (event) {
      case 'file_uploaded':
        return <BiCloudUpload className="text-blue-600" />
      case 'authorized_access':
        return <BiCheckCircle className="text-green-600" />
      case 'unauthorized_access_attempt':
        return <BiXCircle className="text-red-600" />
      case 'decryption_failed':
        return <BiErrorAlt className="text-yellow-600" />
      default:
        return <BiFile className="text-blue-600" />
    }
  }

  const getEventColor = (event: string) => {
    switch (event) {
      case 'file_uploaded':
        return 'bg-blue-500'
      case 'authorized_access':
        return 'bg-green-500'
      case 'unauthorized_access_attempt':
        return 'bg-red-500'
      case 'decryption_failed':
        return 'bg-yellow-500'
      default:
        return 'bg-blue-500'
    }
  }

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* File Information Card */}
      <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-xl p-6 border border-blue-200 dark:border-blue-800">
        <div className="bg-blue-600 text-white rounded-lg p-4 -mt-6 -mx-6 mb-6">
          <h2 className="text-xl font-bold flex items-center space-x-2">
            <BiShield />
            <span>Security Audit Trail</span>
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h6 className="text-blue-600 dark:text-blue-400 font-semibold mb-3">File Information</h6>
            <ul className="space-y-2 text-gray-700 dark:text-gray-300">
              <li><strong>File ID:</strong> {auditData.file_id}</li>
              <li><strong>Filename:</strong> {auditData.filename}</li>
              <li><strong>Owner:</strong> {auditData.owner}</li>
              <li><strong>Authorized Users:</strong> {auditData.authorized_users.join(', ') || 'Owner only'}</li>
            </ul>
          </div>
          <div>
            <h6 className="text-blue-600 dark:text-blue-400 font-semibold mb-3">Security Status</h6>
            <ul className="space-y-2 text-gray-700 dark:text-gray-300">
              <li>
                <strong>Data Confidentiality:</strong>{' '}
                <span
                  className={`px-2 py-1 rounded text-sm ${
                    auditData.security_verification.data_confidentiality === 'maintained'
                      ? 'bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200'
                      : 'bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200'
                  }`}
                >
                  {auditData.security_verification.data_confidentiality}
                </span>
              </li>
              <li>
                <strong>Access Control:</strong>{' '}
                <span
                  className={`px-2 py-1 rounded text-sm ${
                    auditData.security_verification.access_control === 'enforced'
                      ? 'bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200'
                      : 'bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200'
                  }`}
                >
                  {auditData.security_verification.access_control}
                </span>
              </li>
              <li>
                <strong>Cryptographic Verification:</strong>{' '}
                <span
                  className={`px-2 py-1 rounded text-sm ${
                    auditData.security_verification.cryptographic_verification === 'verified'
                      ? 'bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200'
                      : 'bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200'
                  }`}
                >
                  {auditData.security_verification.cryptographic_verification}
                </span>
              </li>
            </ul>
          </div>
        </div>
      </div>

      {/* Security Events Summary */}
      <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-xl p-6 border border-cyan-200 dark:border-cyan-800">
        <div className="bg-cyan-600 text-white rounded-lg p-4 -mt-6 -mx-6 mb-6">
          <h6 className="font-bold flex items-center space-x-2">
            {/* <BiGraphUp /> */}
            <span>Security Events Summary</span>
          </h6>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-slate-50 dark:bg-slate-700 rounded-lg p-4 text-center">
            <h3 className="text-3xl font-bold text-green-600 mb-1">
              {auditData.security_verification.security_events.successful_accesses}
            </h3>
            <p className="text-gray-600 dark:text-gray-400 text-sm">Successful Accesses</p>
          </div>
          <div className="bg-slate-50 dark:bg-slate-700 rounded-lg p-4 text-center">
            <h3 className="text-3xl font-bold text-red-600 mb-1">
              {auditData.security_verification.security_events.unauthorized_attempts}
            </h3>
            <p className="text-gray-600 dark:text-gray-400 text-sm">Unauthorized Attempts</p>
          </div>
          <div className="bg-slate-50 dark:bg-slate-700 rounded-lg p-4 text-center">
            <h3 className="text-3xl font-bold text-yellow-600 mb-1">
              {auditData.security_verification.security_events.failed_decryptions}
            </h3>
            <p className="text-gray-600 dark:text-gray-400 text-sm">Failed Decryptions</p>
          </div>
          <div className="bg-slate-50 dark:bg-slate-700 rounded-lg p-4 text-center">
            <h3 className="text-3xl font-bold text-blue-600 mb-1">
              {auditData.audit_trail.length}
            </h3>
            <p className="text-gray-600 dark:text-gray-400 text-sm">Total Events</p>
          </div>
        </div>
      </div>

      {/* Audit Trail */}
      <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-xl p-6 border border-slate-200 dark:border-slate-700">
        <div className="bg-slate-800 text-white rounded-lg p-4 -mt-6 -mx-6 mb-6">
          <h6 className="font-bold flex items-center space-x-2">
            <BiListUl />
            <span>Complete Audit Trail</span>
          </h6>
        </div>
        {auditData.audit_trail.length > 0 ? (
          <div className="relative pl-8">
            <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-slate-300 dark:bg-slate-600"></div>
            {auditData.audit_trail.map((event, index) => (
              <div key={index} className="relative mb-6">
                <div className={`absolute left-0 top-1 w-3 h-3 rounded-full border-2 border-white dark:border-slate-800 ${getEventColor(event.event)}`}></div>
                <div className="ml-6 bg-slate-50 dark:bg-slate-700 rounded-lg p-4 border-l-4 border-blue-600">
                  <div className="flex justify-between items-start mb-2">
                    <div className="flex items-center space-x-2">
                      {getEventIcon(event.event)}
                      <h6 className="font-semibold text-gray-800 dark:text-white">
                        {event.event.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                      </h6>
                    </div>
                    <small className="text-gray-500 dark:text-gray-400">{event.timestamp}</small>
                  </div>
                  <p className="text-gray-700 dark:text-gray-300 mb-1">{event.description}</p>
                  {event.user && (
                    <small className="text-gray-600 dark:text-gray-400">User: {event.user}</small>
                  )}
                  {event.reason && (
                    <div className="mt-1">
                      <small className="text-gray-600 dark:text-gray-400">Reason: {event.reason}</small>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500 dark:text-gray-400">
            <BiFile className="text-5xl mx-auto mb-3" />
            <p>No security events recorded for this file.</p>
          </div>
        )}
      </div>

      {/* Actions */}
      <div className="flex justify-center space-x-4">
        <Link
          to="/files"
          className="px-6 py-3 bg-slate-600 text-white rounded-lg hover:bg-slate-700 transition-colors flex items-center space-x-2"
        >
          <BiChevronLeft />
          <span>Back to Files</span>
        </Link>
        <Link
          to={`/decrypt/${fileId}`}
          className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-2"
        >
          <BiLockOpen />
          <span>Decrypt File</span>
        </Link>
      </div>
    </div>
  )
}

