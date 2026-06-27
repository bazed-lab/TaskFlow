import { useState, useEffect } from 'react'
import type { User } from '../App'
import ProfileModal from './ProfileModal'

type Props = {
  user: User
  onLogout: () => void
  onNavigate: (hash: string) => void
}

export default function Navbar({ user, onLogout, onNavigate }: Props) {
  const [showProfile, setShowProfile] = useState(false)
  const [dark, setDark] = useState(() => localStorage.getItem('theme') === 'dark')

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', dark ? 'dark' : 'light')
    localStorage.setItem('theme', dark ? 'dark' : 'light')
  }, [dark])

  return (
    <nav className="navbar">
      <button className="navbar-brand" onClick={() => onNavigate('#projects')}>
        TaskFlow
      </button>
      <div className="navbar-right">
        <button className="btn btn-ghost btn-sm theme-toggle" onClick={() => setDark(!dark)} title={dark ? 'Светлая тема' : 'Тёмная тема'}>
          {dark ? '☀️' : '🌙'}
        </button>
        <button className="navbar-user-btn" onClick={() => setShowProfile(true)}>
          <span className="navbar-user-avatar">{user.username[0].toUpperCase()}</span>
          <div style={{ textAlign: 'left' }}>
            <strong>{user.username}</strong>
            <div style={{ fontSize: 11, color: 'var(--text-secondary)' }}>{user.handle}</div>
          </div>
        </button>
        <button className="btn btn-secondary btn-sm" onClick={onLogout}>
          Выйти
        </button>
      </div>
      {showProfile && <ProfileModal user={user} onClose={() => setShowProfile(false)} onUpdate={(updated) => { setShowProfile(false); window.location.reload() }} />}
    </nav>
  )
}
