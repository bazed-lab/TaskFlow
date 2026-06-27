import { useState } from 'react'
import { api } from '../api/client'
import type { User } from '../App'

type Props = {
  onLogin: (user: User, access_token: string, refresh_token: string) => void
}

export default function RegisterForm({ onLogin }: Props) {
  const [username, setUsername] = useState('')
  const [handle, setHandle] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setSubmitting(true)
    try {
      await api.signup({ email, password, username, handle })
      const tokens = await api.login({ email, password })
      const me = await api.getMe()
      onLogin(me, tokens.access_token, tokens.refresh_token)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Registration failed')
    }
    setSubmitting(false)
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h1>Регистрация</h1>
        <p>Создайте новый аккаунт</p>
        {error && <div className="form-error">{error}</div>}
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Имя пользователя</label>
            <input type="text" value={username} onChange={(e) => setUsername(e.target.value)} placeholder="username" required minLength={3} />
          </div>
          <div className="form-group">
            <label>Handle (@ник)</label>
            <input type="text" value={handle} onChange={(e) => setHandle(e.target.value)} placeholder="@username" required minLength={2} pattern="^@[a-zA-Z0-9_.-]+$" />
          </div>
          <div className="form-group">
            <label>Email</label>
            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="your@email.com" required />
          </div>
          <div className="form-group">
            <label>Пароль</label>
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="••••••••" required minLength={8} />
          </div>
          <button className="btn btn-primary" style={{ width: '100%' }} disabled={submitting}>
            {submitting ? 'Регистрация...' : 'Зарегистрироваться'}
          </button>
        </form>
        <div className="form-footer">
          Уже есть аккаунт? <a href="#login">Войти</a>
        </div>
      </div>
    </div>
  )
}
