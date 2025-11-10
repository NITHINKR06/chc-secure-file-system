import { ReactNode, useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { 
  BiShield, BiHome, BiCloudUpload, BiFile, BiNetworkChart, 
  BiLogIn, BiUserPlus, BiUser, BiLogOut 
} from 'react-icons/bi'

interface LayoutProps {
  children: ReactNode
  currentUser?: {
    username: string
    email: string
    role: string
  } | null
}

export default function Layout({ children, currentUser }: LayoutProps) {
  const location = useLocation()
  const [showUserMenu, setShowUserMenu] = useState(false)
  const [showMobileMenu, setShowMobileMenu] = useState(false)

  const isActive = (path: string) => location.pathname === path

  return (
    <div className="min-h-screen flex flex-col bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800">
      {/* Navigation Bar */}
      <nav className="bg-white dark:bg-slate-800 shadow-lg border-b border-slate-200 dark:border-slate-700">
        <div className="container mx-auto px-4">
          <div className="flex items-center justify-between h-16">
            {/* Brand */}
            <Link to="/" className="flex items-center space-x-2 text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              <BiShield className="text-blue-600" />
              <span>CHC Secure File Management</span>
            </Link>

            {/* Navigation Links */}
            <div className="hidden md:flex items-center space-x-1">
              <Link
                to="/"
                className={`px-4 py-2 rounded-lg transition-colors flex items-center space-x-1 ${
                  isActive('/') 
                    ? 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300' 
                    : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-slate-700'
                }`}
              >
                <BiHome />
                <span>Home</span>
              </Link>

              {currentUser ? (
                <>
                  <Link
                    to="/upload"
                    className={`px-4 py-2 rounded-lg transition-colors flex items-center space-x-1 ${
                      isActive('/upload') 
                        ? 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300' 
                        : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-slate-700'
                    }`}
                  >
                    <BiCloudUpload />
                    <span>Upload</span>
                  </Link>
                  <Link
                    to="/files"
                    className={`px-4 py-2 rounded-lg transition-colors flex items-center space-x-1 ${
                      isActive('/files') 
                        ? 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300' 
                        : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-slate-700'
                    }`}
                  >
                    <BiFile />
                    <span>Files</span>
                  </Link>
                  <Link
                    to="/blockchain"
                    className={`px-4 py-2 rounded-lg transition-colors flex items-center space-x-1 ${
                      isActive('/blockchain') 
                        ? 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300' 
                        : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-slate-700'
                    }`}
                  >
                    <BiNetworkChart />
                    <span>Blockchain</span>
                  </Link>
                  
                  {/* User Dropdown */}
                  <div className="relative ml-2">
                    <button 
                      onClick={() => setShowUserMenu(!showUserMenu)}
                      className="px-4 py-2 rounded-lg transition-colors flex items-center space-x-1 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-slate-700"
                    >
                      <BiUser />
                      <span>{currentUser.username}</span>
                    </button>
                    {showUserMenu && (
                      <div className="absolute right-0 mt-2 w-56 bg-white dark:bg-slate-800 rounded-lg shadow-lg border border-slate-200 dark:border-slate-700 z-50">
                        <div className="py-2">
                          <div className="px-4 py-2 text-sm text-gray-700 dark:text-gray-300 border-b border-slate-200 dark:border-slate-700">
                            <div className="font-medium">{currentUser.email}</div>
                            <div className="text-xs text-gray-500 dark:text-gray-400">Role: {currentUser.role}</div>
                          </div>
                          <Link
                            to="/logout"
                            onClick={() => setShowUserMenu(false)}
                            className="block px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-slate-700 flex items-center space-x-2"
                          >
                            <BiLogOut />
                            <span>Logout</span>
                          </Link>
                        </div>
                      </div>
                    )}
                  </div>
                </>
              ) : (
                <>
                  <Link
                    to="/login"
                    className={`px-4 py-2 rounded-lg transition-colors flex items-center space-x-1 ${
                      isActive('/login') 
                        ? 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300' 
                        : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-slate-700'
                    }`}
                  >
                    <BiLogIn />
                    <span>Login</span>
                  </Link>
                  <Link
                    to="/register"
                    className={`px-4 py-2 rounded-lg transition-colors flex items-center space-x-1 ${
                      isActive('/register') 
                        ? 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300' 
                        : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-slate-700'
                    }`}
                  >
                    <BiUserPlus />
                    <span>Register</span>
                  </Link>
                </>
              )}
            </div>

            {/* Mobile Menu Button */}
            <button 
              onClick={() => setShowMobileMenu(!showMobileMenu)}
              className="md:hidden text-gray-700 dark:text-gray-300"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
          </div>

          {/* Mobile Menu */}
          {showMobileMenu && (
            <div className="md:hidden mt-4 pb-4 border-t border-slate-200 dark:border-slate-700 pt-4">
              <div className="flex flex-col space-y-2">
                <Link
                  to="/"
                  onClick={() => setShowMobileMenu(false)}
                  className={`px-4 py-2 rounded-lg transition-colors ${
                    isActive('/') 
                      ? 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300' 
                      : 'text-gray-700 dark:text-gray-300'
                  }`}
                >
                  <BiHome className="inline mr-2" />
                  Home
                </Link>
                {currentUser ? (
                  <>
                    <Link
                      to="/upload"
                      onClick={() => setShowMobileMenu(false)}
                      className={`px-4 py-2 rounded-lg transition-colors ${
                        isActive('/upload') 
                          ? 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300' 
                          : 'text-gray-700 dark:text-gray-300'
                      }`}
                    >
                      <BiCloudUpload className="inline mr-2" />
                      Upload
                    </Link>
                    <Link
                      to="/files"
                      onClick={() => setShowMobileMenu(false)}
                      className={`px-4 py-2 rounded-lg transition-colors ${
                        isActive('/files') 
                          ? 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300' 
                          : 'text-gray-700 dark:text-gray-300'
                      }`}
                    >
                      <BiFile className="inline mr-2" />
                      Files
                    </Link>
                    <Link
                      to="/blockchain"
                      onClick={() => setShowMobileMenu(false)}
                      className={`px-4 py-2 rounded-lg transition-colors ${
                        isActive('/blockchain') 
                          ? 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300' 
                          : 'text-gray-700 dark:text-gray-300'
                      }`}
                    >
                      <BiNetworkChart className="inline mr-2" />
                      Blockchain
                    </Link>
                    <div className="px-4 py-2 text-gray-700 dark:text-gray-300 border-t border-slate-200 dark:border-slate-700 mt-2 pt-2">
                      <div className="font-medium">{currentUser.username}</div>
                      <div className="text-xs text-gray-500 dark:text-gray-400">{currentUser.email}</div>
                    </div>
                    <Link
                      to="/logout"
                      onClick={() => setShowMobileMenu(false)}
                      className="px-4 py-2 text-gray-700 dark:text-gray-300"
                    >
                      <BiLogOut className="inline mr-2" />
                      Logout
                    </Link>
                  </>
                ) : (
                  <>
                    <Link
                      to="/login"
                      onClick={() => setShowMobileMenu(false)}
                      className={`px-4 py-2 rounded-lg transition-colors ${
                        isActive('/login') 
                          ? 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300' 
                          : 'text-gray-700 dark:text-gray-300'
                      }`}
                    >
                      <BiLogIn className="inline mr-2" />
                      Login
                    </Link>
                    <Link
                      to="/register"
                      onClick={() => setShowMobileMenu(false)}
                      className={`px-4 py-2 rounded-lg transition-colors ${
                        isActive('/register') 
                          ? 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300' 
                          : 'text-gray-700 dark:text-gray-300'
                      }`}
                    >
                      <BiUserPlus className="inline mr-2" />
                      Register
                    </Link>
                  </>
                )}
              </div>
            </div>
          )}
        </div>
      </nav>

      {/* Flash Messages Area - You can add toast notifications here later */}
      <div className="container mx-auto px-4 mt-4">
        {/* Flash messages will go here */}
      </div>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8 flex-1">
        {children}
      </main>

      {/* Footer */}
      <footer className="bg-white dark:bg-slate-800 border-t border-slate-200 dark:border-slate-700 mt-auto">
        <div className="container mx-auto px-4 py-4 text-center">
          <p className="text-gray-700 dark:text-gray-300 mb-2">
            <BiShield className="inline mr-2" />
            <strong>CHC Secure File Management System</strong> - Academic Demonstration
          </p>
          <small className="text-gray-500 dark:text-gray-400">
            Secure File Storage with Contextual Hash Chain Encryption & Blockchain Integration
          </small>
        </div>
      </footer>
    </div>
  )
}

