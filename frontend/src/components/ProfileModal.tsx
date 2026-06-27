import { useState } from 'react'
import { api } from '../api/client'
import type { User } from '../App'

type Props = {
  user: User
  onClose: () => void
  onUpdate: (user: User) => void
}

export default function ProfileModal({ user, onClose, onUpdate }: Props) {
  const [username, setUsername] = useState(user.username)
  const [handle, setHandle] = useState(user.handle)
  const [email, setEmail] = useState(user.email)
  const [password, setPassword] = useState('')
  const [oldPassword, setOldPassword] = useState('')
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setSuccess('')
    setSubmitting(true)
    try {
      const data: Record<string, unknown> = {}
      if (username !== user.username) data.username = username
      if (handle !== user.handle) data.handle = handle
      if (email !== user.email) data.email = email
      if (password) {
        if (!oldPassword) {
          setError('Введите старый пароль для смены пароля')
          setSubmitting(false)
          return
        }
        data.password = password
        data.old_password = oldPassword
      }
      if (Object.keys(data).length === 0) {
        setError('Нет изменений')
        setSubmitting(false)
        return
      }
      const updated = await api.updateMe(data)
      onUpdate(updated)
      setSuccess('Профиль обновлён')
      setPassword('')
      setOldPassword('')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка обновления')
    }
    setSubmitting(false)
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()} style={{ maxWidth: 440 }}>
        <button className="modal-close" onClick={onClose}>✕</button>
        <h2>Профиль</h2>
        {error && <div className="form-error">{error}</div>}
        {success && <div className="form-success">{success}</div>}
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Имя пользователя</label>
            <input type="text" value={username} onChange={(e) => setUsername(e.target.value)} required />
          </div>
          <div className="form-group">
            <label>Handle</label>
            <input type="text" value={handle} onChange={(e) => setHandle(e.target.value)} required minLength={2} pattern="^@[a-zA-Z0-9_.-]+$" />
          </div>
          <div className="form-group">
            <label>Email</label>
            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
          </div>
          <hr className="form-divider" />
          <div className="form-group">
            <label>Новый пароль (оставьте пустым, чтобы не менять)</label>
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Новый пароль" />
          </div>
          <div className="form-group">
            <label>Старый пароль</label>
            <input type="password" value={oldPassword} onChange={(e) => setOldPassword(e.target.value)} placeholder="Старый пароль" />
          </div>
          <div className="modal-actions">
            <button type="button" className="btn btn-secondary" onClick={onClose}>Закрыть</button>
            <button type="submit" className="btn btn-primary" disabled={submitting}>
              {submitting ? 'Сохранение...' : 'Сохранить'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
