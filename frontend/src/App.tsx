import { useEffect, useState, useCallback } from 'react'
import { api } from './api/client'
import Navbar from './components/Navbar'
import LoginForm from './components/LoginForm'
import RegisterForm from './components/RegisterForm'
import ProjectList from './components/ProjectList'
import ProjectDetail from './components/ProjectDetail'

export type User = {
  id: number
  email: string
  username: string
  handle: string
  is_active: boolean
  is_superuser: boolean
}

type Page = { name: 'login' } | { name: 'register' } | { name: 'projects' } | { name: 'project'; id: string }

function getPageFromHash(): Page {
  const hash = window.location.hash.replace('#', '')
  if (hash === 'login') return { name: 'login' }
  if (hash === 'register') return { name: 'register' }
  if (hash.startsWith('project/')) return { name: 'project', id: hash.split('/')[1] }
  return { name: 'projects' }
}

export default function App() {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const [page, setPage] = useState<Page>(() => getPageFromHash())

  useEffect(() => {
    const onHashChange = () => setPage(getPageFromHash())
    window.addEventListener('hashchange', onHashChange)
    return () => window.removeEventListener('hashchange', onHashChange)
  }, [])

  const checkAuth = useCallback(async () => {
    const token = localStorage.getItem('access_token')
    if (!token) {
      setUser(null)
      setLoading(false)
      if (page.name === 'projects' || page.name === 'project') {
        window.location.hash = '#login'
      }
      return
    }
    try {
      const me = await api.getMe()
      setUser(me)
    } catch {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      setUser(null)
      if (page.name !== 'login' && page.name !== 'register') {
        window.location.hash = '#login'
      }
    }
    setLoading(false)
  }, [page.name])

  useEffect(() => {
    checkAuth()
  }, [checkAuth])

  const handleLogin = (user: User, access_token: string, refresh_token: string) => {
    localStorage.setItem('access_token', access_token)
    localStorage.setItem('refresh_token', refresh_token)
    setUser(user)
    window.location.hash = '#projects'
  }

  const handleLogout = () => {
    const rt = localStorage.getItem('refresh_token')
    if (rt) api.logout(rt).catch(() => {})
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    setUser(null)
    window.location.hash = '#login'
  }

  if (loading) {
    return (
      <div className="app-loading">
        <div className="spinner" />
      </div>
    )
  }

  if (!user && page.name !== 'login' && page.name !== 'register') {
    window.location.hash = '#login'
    return null
  }

  return (
    <div className="app">
      {user && <Navbar user={user} onLogout={handleLogout} onNavigate={(p) => { window.location.hash = p }} />}
      <main className="main-content">
        {page.name === 'login' && <LoginForm onLogin={handleLogin} />}
        {page.name === 'register' && <RegisterForm onLogin={handleLogin} />}
        {page.name === 'projects' && user && <ProjectList user={user} />}
        {page.name === 'project' && user && <ProjectDetail projectId={page.id} user={user} />}
      </main>
    </div>
  )
}
