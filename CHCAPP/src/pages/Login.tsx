import { useState, FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { BiLogIn, BiUser, BiLock, BiInfoCircle, BiErrorAlt } from 'react-icons/bi'
import { apiPost, setAuthToken } from '../utils/api'

export default function Login() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const navigate = useNavigate()

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    
    try {
      const result = await apiPost('/api/login', { username, password })
      if (result.success) {
        setAuthToken(result.session_token, result.user)
        // Trigger storage event to update App.tsx
        window.dispatchEvent(new Event('storage'))
        // Small delay to ensure state updates
        setTimeout(() => navigate('/files'), 100)
      } else {
        setError(result.message || 'Login failed')
      }
    } catch (err: any) {
      setError(err.message || 'Login failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      {/* Login Card */}
      <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-xl p-8 border border-slate-200 dark:border-slate-700">
        <div className="mb-6">
          <h2 className="text-2xl font-bold text-gray-800 dark:text-white flex items-center space-x-2">
            <BiLogIn className="text-blue-600" />
            <span>Login to File Management System</span>
          </h2>
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-2">
            Access your secure files with blockchain-protected encryption
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
              placeholder="Enter your username"
              autoComplete="username"
              required
              autoFocus
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
              placeholder="Enter your password"
              autoComplete="current-password"
              required
            />
          </div>

          {/* Error Message */}
          {error && (
            <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 flex items-center space-x-2 text-red-700 dark:text-red-300">
              <BiErrorAlt />
              <span>{error}</span>
            </div>
          )}

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-semibold py-3 rounded-lg hover:from-blue-700 hover:to-indigo-700 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
          >
            {loading ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                <span>Logging in...</span>
              </>
            ) : (
              <>
                <BiLogIn />
                <span>Login</span>
              </>
            )}
          </button>

          {/* Register Link */}
          <div className="text-center">
            <p className="text-gray-600 dark:text-gray-400">
              Don't have an account?{' '}
              <Link to="/register" className="text-blue-600 font-semibold hover:underline">
                Register here
              </Link>
            </p>
          </div>
        </form>
      </div>

      {/* Info Card */}
      <div className="bg-blue-50 dark:bg-blue-900/20 rounded-xl p-6 border border-blue-200 dark:border-blue-800">
        <h5 className="font-bold mb-3 text-blue-800 dark:text-blue-300 flex items-center space-x-2">
          <BiInfoCircle />
          <span>Default Admin Account</span>
        </h5>
        <div className="text-gray-700 dark:text-gray-300 space-y-1">
          <p><strong>Username:</strong> admin</p>
          <p><strong>Password:</strong> admin123</p>
        </div>
        <div className="mt-3 text-sm text-red-600 dark:text-red-400 flex items-center space-x-1">
          <BiErrorAlt />
          <span>Please change the default password after first login!</span>
        </div>
      </div>
    </div>
  )
}

