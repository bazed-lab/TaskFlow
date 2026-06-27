import { useState } from 'react'
import { api } from '../api/client'
import type { User } from '../App'

type Props = {
  onLogin: (user: User, access_token: string, refresh_token: string) => void
}

export default function LoginForm({ onLogin }: Props) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setSubmitting(true)
    try {
      const tokens = await api.login({ email, password })
      const me = await api.getMe()
      onLogin(me, tokens.access_token, tokens.refresh_token)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed')
    }
    setSubmitting(false)
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h1>Вход</h1>
        <p>Войдите в свой аккаунт</p>
        {error && <div className="form-error">{error}</div>}
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Email</label>
            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="your@email.com" required />
          </div>
          <div className="form-group">
            <label>Пароль</label>
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="••••••••" required />
          </div>
          <button className="btn btn-primary" style={{ width: '100%' }} disabled={submitting}>
            {submitting ? 'Вход...' : 'Войти'}
          </button>
        </form>
        <div className="form-footer">
          Нет аккаунта? <a href="#register">Зарегистрироваться</a>
        </div>
      </div>
    </div>
  )
}
