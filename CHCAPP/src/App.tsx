import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { useState } from 'react'
import Layout from './components/Layout'
import Home from './pages/Home'
import Login from './pages/Login'
import Register from './pages/Register'
import Upload from './pages/Upload'
import Files from './pages/Files'
import Decrypt from './pages/Decrypt'
import Blockchain from './pages/Blockchain'
import SecurityAudit from './pages/SecurityAudit'

function App() {
  // Mock user state - replace with actual authentication
  const [currentUser, setCurrentUser] = useState<{
    username: string
    email: string
    role: string
  } | null>(null)

  return (
    <Router>
      <Layout currentUser={currentUser}>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
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
