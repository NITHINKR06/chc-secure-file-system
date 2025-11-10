import { useState, useEffect } from 'react'
import { BiNetworkChart, BiHash, BiCalendar, BiFile, BiUser, BiGroup, BiLink, BiChevronLeft, BiShield, BiCode, BiDownload, BiCheckCircle, BiXCircle } from 'react-icons/bi'

// Mock blockchain data
const mockChain = [
  {
    index: 0,
    timestamp: '2024-01-01 00:00:00',
    file_id: 'genesis',
    owner: null,
    authorized_users: null,
    block_hash: '0'.repeat(64),
    prev_hash: '0'.repeat(64)
  },
  {
    index: 1,
    timestamp: '2024-01-15 10:30:00',
    file_id: 'file123',
    owner: 'admin',
    authorized_users: 'John, Jane',
    block_hash: 'abc123def456ghi789jkl012mno345pqr678stu901vwx234yz5678901234567890',
    prev_hash: '0'.repeat(64)
  }
]

export default function Blockchain() {
  const [chain] = useState(mockChain)
  const [showRawData, setShowRawData] = useState(false)
  const [jsonData, setJsonData] = useState('')

  useEffect(() => {
    setJsonData(JSON.stringify(chain, null, 2))
  }, [chain])

  const chainLength = chain.length
  const isValid = true // Mock validation

  const copyJSON = () => {
    navigator.clipboard.writeText(jsonData)
    alert('Blockchain data copied to clipboard!')
  }

  return (
    <div className="space-y-6">
      {/* Header Card */}
      <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-xl p-6 border border-slate-200 dark:border-slate-700">
        <div className="flex justify-between items-center">
          <h2 className="text-2xl font-bold text-gray-800 dark:text-white flex items-center space-x-2">
            <BiNetworkChart className="text-blue-600" />
            <span>Blockchain Ledger</span>
          </h2>
          <div className="flex space-x-2">
            <span className="px-3 py-1 bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-300 rounded-lg text-sm flex items-center space-x-1">
              <BiLink />
              <span>{chainLength} Blocks</span>
            </span>
            {isValid ? (
              <span className="px-3 py-1 bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300 rounded-lg text-sm flex items-center space-x-1">
                <BiCheckCircle />
                <span>Chain Valid</span>
              </span>
            ) : (
              <span className="px-3 py-1 bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-300 rounded-lg text-sm flex items-center space-x-1">
                <BiXCircle />
                <span>Chain Invalid</span>
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Blockchain Table */}
      {chain.length > 0 ? (
        <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-slate-800 dark:bg-slate-900 text-white">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">
                    <BiHash className="inline mr-1" />
                    Index
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">
                    <BiCalendar className="inline mr-1" />
                    Timestamp
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">
                    <BiFile className="inline mr-1" />
                    File ID
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">
                    <BiUser className="inline mr-1" />
                    Owner
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">
                    <BiGroup className="inline mr-1" />
                    Authorized Users
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">
                    <BiLink className="inline mr-1" />
                    Block Hash
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">
                    <BiChevronLeft className="inline mr-1" />
                    Previous Hash
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white dark:bg-slate-800 divide-y divide-slate-200 dark:divide-slate-700">
                {chain.map((block) => (
                  <tr
                    key={block.index}
                    className={block.index === 0 ? 'bg-cyan-50 dark:bg-cyan-900/20' : ''}
                  >
                    <td className="px-6 py-4 whitespace-nowrap text-center">
                      <span
                        className={`px-2 py-1 rounded text-sm font-medium ${
                          block.index === 0
                            ? 'bg-cyan-600 text-white'
                            : 'bg-slate-600 text-white'
                        }`}
                      >
                        {block.index}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                      {block.timestamp}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {block.file_id === 'genesis' ? (
                        <span className="px-2 py-1 bg-cyan-600 text-white rounded text-sm">
                          <BiFile className="inline mr-1" />
                          Genesis Block
                        </span>
                      ) : (
                        <code className="text-red-600 dark:text-red-400 text-sm">
                          {block.file_id}
                        </code>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {block.owner ? (
                        <span className="px-2 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded text-sm">
                          {block.owner}
                        </span>
                      ) : (
                        <span className="text-gray-400">-</span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                      {block.authorized_users || <span className="text-gray-400">-</span>}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <code className="text-blue-600 dark:text-blue-400 text-xs font-mono">
                        {block.block_hash.substring(0, 20)}...
                      </code>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <code className="text-gray-600 dark:text-gray-400 text-xs font-mono">
                        {block.prev_hash.substring(0, 20)}...
                      </code>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : (
        <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-xl p-12 border border-slate-200 dark:border-slate-700 text-center">
          <BiNetworkChart className="text-6xl mx-auto mb-4 text-gray-400" />
          <h5 className="text-xl font-semibold text-gray-600 dark:text-gray-400 mb-2">
            Blockchain Not Initialized
          </h5>
          <p className="text-gray-500">The blockchain will be created when you upload your first file</p>
        </div>
      )}

      {/* Blockchain Visualization */}
      {chain.length > 1 && (
        <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-xl p-6 border border-slate-200 dark:border-slate-700">
          <h5 className="text-lg font-bold mb-4 text-gray-800 dark:text-white flex items-center space-x-2">
            <BiNetworkChart />
            <span>Chain Visualization</span>
          </h5>
          <div className="flex items-center overflow-x-auto pb-3 space-x-4">
            {chain.map((block, index) => (
              <div key={block.index} className="flex items-center space-x-4">
                <div
                  className={`min-w-[150px] text-center p-4 rounded-lg border-2 ${
                    block.index === 0
                      ? 'bg-cyan-600 text-white border-cyan-700'
                      : 'bg-slate-100 dark:bg-slate-700 text-gray-800 dark:text-white border-slate-300 dark:border-slate-600'
                  }`}
                >
                  <h6 className="font-bold mb-1">Block #{block.index}</h6>
                  <p className="text-xs truncate">
                    {block.file_id === 'genesis'
                      ? 'Genesis'
                      : block.file_id?.substring(0, 8) + '...' || 'N/A'}
                  </p>
                </div>
                {index < chain.length - 1 && (
                  <BiChevronLeft className="text-blue-600 text-2xl" />
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Blockchain Properties */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-xl p-6 border border-green-200 dark:border-green-800">
          <div className="bg-green-600 text-white rounded-lg p-4 -mt-6 -mx-6 mb-6">
            <h5 className="font-bold flex items-center space-x-2">
              <BiShield />
              <span>Security Properties</span>
            </h5>
          </div>
          <ul className="space-y-2 text-gray-700 dark:text-gray-300">
            <li className="flex items-start space-x-2">
              <BiCheckCircle className="text-green-600 mt-1 flex-shrink-0" />
              <span><strong>Immutability:</strong> Each block is cryptographically linked</span>
            </li>
            <li className="flex items-start space-x-2">
              <BiCheckCircle className="text-green-600 mt-1 flex-shrink-0" />
              <span><strong>Integrity:</strong> SHA-256 hash ensures data integrity</span>
            </li>
            <li className="flex items-start space-x-2">
              <BiCheckCircle className="text-green-600 mt-1 flex-shrink-0" />
              <span><strong>Traceability:</strong> Complete audit trail of all uploads</span>
            </li>
            <li className="flex items-start space-x-2">
              <BiCheckCircle className="text-green-600 mt-1 flex-shrink-0" />
              <span><strong>Context:</strong> Provides unique context for encryption</span>
            </li>
          </ul>
        </div>

        <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-xl p-6 border border-slate-200 dark:border-slate-700">
          <h5 className="font-bold mb-4 text-gray-800 dark:text-white flex items-center space-x-2">
            <BiFile />
            <span>Blockchain Details</span>
          </h5>
          <dl className="space-y-3">
            <div className="flex justify-between">
              <dt className="text-gray-600 dark:text-gray-400">Hash Algorithm:</dt>
              <dd className="font-mono text-sm bg-slate-100 dark:bg-slate-700 px-2 py-1 rounded">
                SHA-256
              </dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-gray-600 dark:text-gray-400">Storage Format:</dt>
              <dd className="font-mono text-sm bg-slate-100 dark:bg-slate-700 px-2 py-1 rounded">
                JSON
              </dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-gray-600 dark:text-gray-400">Chain Length:</dt>
              <dd className="px-2 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded text-sm font-medium">
                {chainLength} blocks
              </dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-gray-600 dark:text-gray-400">Chain Status:</dt>
              <dd>
                {isValid ? (
                  <span className="px-2 py-1 bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 rounded text-sm font-medium">
                    Valid
                  </span>
                ) : (
                  <span className="px-2 py-1 bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200 rounded text-sm font-medium">
                    Invalid
                  </span>
                )}
              </dd>
            </div>
          </dl>
        </div>
      </div>

      {/* Raw JSON View */}
      <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-xl p-6 border border-slate-200 dark:border-slate-700">
        <div className="flex justify-between items-center mb-4">
          <h5 className="font-bold text-gray-800 dark:text-white flex items-center space-x-2">
            <BiCode />
            <span>Raw Blockchain Data</span>
          </h5>
          <button
            onClick={() => setShowRawData(!showRawData)}
            className="px-4 py-2 bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-300 rounded-lg hover:bg-slate-200 dark:hover:bg-slate-600 transition-colors flex items-center space-x-2"
          >
            <BiCode />
            <span>Toggle View</span>
          </button>
        </div>
        {showRawData && (
          <div className="space-y-4">
            <pre className="bg-slate-900 text-green-400 p-4 rounded-lg overflow-x-auto max-h-96 overflow-y-auto text-sm">
              <code>{jsonData}</code>
            </pre>
            <div className="flex space-x-2">
              <button
                onClick={copyJSON}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-2"
              >
                <BiFile />
                <span>Copy JSON</span>
              </button>
              <button className="px-4 py-2 bg-slate-600 text-white rounded-lg hover:bg-slate-700 transition-colors flex items-center space-x-2">
                <BiDownload />
                <span>Download JSON</span>
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

