import { useState, FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { BiUserPlus, BiUser, BiEnvelope, BiLock, BiShield, BiCheckCircle } from 'react-icons/bi'

export default function Register() {
  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setLoading(true)
    // TODO: Implement registration logic
    setTimeout(() => setLoading(false), 2000)
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      {/* Register Card */}
      <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-xl p-8 border border-slate-200 dark:border-slate-700">
        <div className="mb-6">
          <h2 className="text-2xl font-bold text-gray-800 dark:text-white flex items-center space-x-2">
            <BiUserPlus className="text-blue-600" />
            <span>Create New Account</span>
          </h2>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Username */}
          <div>
            <label htmlFor="username" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              <BiUser className="inline mr-2 text-blue-600" />
              Username <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              id="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full px-4 py-3 border border-slate-300 dark:border-slate-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-slate-700 dark:text-white"
              placeholder="Choose a username"
              required
              autoFocus
            />
            <p className="mt-2 text-sm text-gray-500 dark:text-gray-400 flex items-center space-x-1">
              <BiUser />
              <span>This will be used to identify you as the file owner</span>
            </p>
          </div>

          {/* Email */}
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              <BiEnvelope className="inline mr-2 text-blue-600" />
              Email <span className="text-red-500">*</span>
            </label>
            <input
              type="email"
              id="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-4 py-3 border border-slate-300 dark:border-slate-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-slate-700 dark:text-white"
              placeholder="Enter your email"
              required
            />
          </div>

          {/* Password */}
          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              <BiLock className="inline mr-2 text-blue-600" />
              Password <span className="text-red-500">*</span>
            </label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-3 border border-slate-300 dark:border-slate-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-slate-700 dark:text-white"
              placeholder="Choose a password (min 6 characters)"
              required
              minLength={6}
            />
            <p className="mt-2 text-sm text-gray-500 dark:text-gray-400 flex items-center space-x-1">
              <BiShield />
              <span>Password must be at least 6 characters long</span>
            </p>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-semibold py-3 rounded-lg hover:from-blue-700 hover:to-indigo-700 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
          >
            {loading ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                <span>Registering...</span>
              </>
            ) : (
              <>
                <BiUserPlus />
                <span>Register</span>
              </>
            )}
          </button>

          {/* Login Link */}
          <div className="text-center">
            <p className="text-gray-600 dark:text-gray-400">
              Already have an account?{' '}
              <Link to="/login" className="text-blue-600 font-semibold hover:underline">
                Login here
              </Link>
            </p>
          </div>
        </form>
      </div>

      {/* Security Notice */}
      <div className="bg-green-50 dark:bg-green-900/20 rounded-xl p-6 border border-green-200 dark:border-green-800">
        <h5 className="font-bold mb-3 text-green-800 dark:text-green-300 flex items-center space-x-2">
          <BiShield />
          <span>Security Features</span>
        </h5>
        <ul className="space-y-2 text-gray-700 dark:text-gray-300">
          <li className="flex items-start space-x-2">
            <BiCheckCircle className="text-green-600 mt-1 flex-shrink-0" />
            <span><strong>Secure Password Storage:</strong> Passwords are hashed using PBKDF2-SHA256</span>
          </li>
          <li className="flex items-start space-x-2">
            <BiCheckCircle className="text-green-600 mt-1 flex-shrink-0" />
            <span><strong>Session Management:</strong> Secure session tokens for authentication</span>
          </li>
          <li className="flex items-start space-x-2">
            <BiCheckCircle className="text-green-600 mt-1 flex-shrink-0" />
            <span><strong>Access Control:</strong> Only authorized users can decrypt files</span>
          </li>
        </ul>
      </div>
    </div>
  )
}

