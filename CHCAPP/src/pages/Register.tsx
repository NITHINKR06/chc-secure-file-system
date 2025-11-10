import { useState, FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { BiUserPlus, BiUser, BiEnvelope, BiLock, BiShield, BiCheckCircle, BiErrorAlt } from 'react-icons/bi'
import { apiPost } from '../utils/api'

export default function Register() {
  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)
  const navigate = useNavigate()

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    setSuccess(false)
    
    try {
      const result = await apiPost('/api/register', { username, email, password })
      if (result.success) {
        setSuccess(true)
        setTimeout(() => {
          navigate('/login')
        }, 2000)
      } else {
        setError(result.message || 'Registration failed')
      }
    } catch (err: any) {
      setError(err.message || 'Registration failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      {/* Register Card */}
      <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-xl p-8 border border-slate-200 dark:border-slate-700">
        <div className="mb-6">
          <h2 className="text-2xl font-bold text-gray-800 dark:text-white flex items-center space-x-2">
            <BiUserPlus className="text-blue-600" />
            <span>Create File Management Account</span>
          </h2>
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-2">
            Register to start securely managing your files with CHC encryption
          </p>
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
              autoComplete="username"
              required
              autoFocus
            />
            <p className="mt-2 text-sm text-gray-500 dark:text-gray-400 flex items-center space-x-1">
              <BiUser />
              <span>This username will identify you as the file owner in the secure file management system</span>
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
              autoComplete="email"
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
              autoComplete="new-password"
              required
              minLength={6}
            />
            <p className="mt-2 text-sm text-gray-500 dark:text-gray-400 flex items-center space-x-1">
              <BiShield />
              <span>Password must be at least 6 characters long</span>
            </p>
          </div>

          {/* Error Message */}
          {error && (
            <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 flex items-center space-x-2 text-red-700 dark:text-red-300">
              <BiErrorAlt />
              <span>{error}</span>
            </div>
          )}

          {/* Success Message */}
          {success && (
            <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4 flex items-center space-x-2 text-green-700 dark:text-green-300">
              <BiCheckCircle />
              <span>Registration successful! Redirecting to login...</span>
            </div>
          )}

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading || success}
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
            <span><strong>File Access Control:</strong> Only authorized users can access and decrypt your files</span>
          </li>
        </ul>
      </div>
    </div>
  )
}

