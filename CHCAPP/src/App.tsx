import { BrowserRouter as Router, Routes, Route, useNavigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import Layout from './components/Layout'
import Home from './pages/Home'
import Login from './pages/Login'
import Register from './pages/Register'
import Upload from './pages/Upload'
import Files from './pages/Files'
import Decrypt from './pages/Decrypt'
import Blockchain from './pages/Blockchain'
import SecurityAudit from './pages/SecurityAudit'
import { getCurrentUser, clearAuth, apiPost } from './utils/api'

function LogoutPage() {
  const navigate = useNavigate()
  
  useEffect(() => {
    const handleLogout = async () => {
      try {
        const token = localStorage.getItem('chc_session_token')
        if (token) {
          await apiPost('/api/logout', { session_token: token })
        }
      } catch (err) {
        console.error('Logout error:', err)
      } finally {
        clearAuth()
        navigate('/login')
      }
    }
    handleLogout()
  }, [navigate])
  
  return <div className="text-center py-8">Logging out...</div>
}

function App() {
  const [currentUser, setCurrentUser] = useState<{
    username: string
    email: string
    role: string
  } | null>(null)

  useEffect(() => {
    // Load user from localStorage on mount
    const user = getCurrentUser()
    if (user) {
      setCurrentUser(user)
    }
    
    // Listen for storage changes (when user logs in from another tab)
    const handleStorageChange = () => {
      const user = getCurrentUser()
      setCurrentUser(user)
    }
    
    window.addEventListener('storage', handleStorageChange)
    return () => window.removeEventListener('storage', handleStorageChange)
  }, [])
  
  // Update user state when localStorage changes
  useEffect(() => {
    const checkAuth = () => {
      const user = getCurrentUser()
      setCurrentUser(user)
    }
    
    // Check auth every second (simple polling)
    const interval = setInterval(checkAuth, 1000)
    return () => clearInterval(interval)
  }, [])

  return (
    <Router>
      <Layout currentUser={currentUser}>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/logout" element={<LogoutPage />} />
          <Route path="/upload" element={<Upload />} />
          <Route path="/files" element={<Files />} />
          <Route path="/decrypt/:fileId" element={<Decrypt />} />
          <Route path="/blockchain" element={<Blockchain />} />
          <Route path="/security/:fileId" element={<SecurityAudit />} />
        </Routes>
      </Layout>
    </Router>
  )
}

export default App
