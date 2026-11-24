import { useEffect, useState, type FormEvent } from 'react'
import { authApi } from '../api/affordable'
import type { User } from '../types'

interface AuthModalProps {
  onClose: () => void
  onAuthenticated: (user: User) => void
}

export function AuthModal({ onClose, onAuthenticated }: AuthModalProps) {
  const [mode, setMode] = useState<'login' | 'register'>('login')
  const [pending, setPending] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    const previousOverflow = document.body.style.overflow
    const handleKey = (event: KeyboardEvent) => { if (event.key === 'Escape') onClose() }
    document.body.style.overflow = 'hidden'
    document.addEventListener('keydown', handleKey)
    return () => {
      document.body.style.overflow = previousOverflow
      document.removeEventListener('keydown', handleKey)
    }
  }, [onClose])

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setPending(true)
    setError('')
    const data = new FormData(event.currentTarget)
    try {
      const email = String(data.get('email'))
      const password = String(data.get('password'))
      const user =
        mode === 'login'
          ? await authApi.login(email, password)
          : await authApi.register(String(data.get('name')), email, password)
      onAuthenticated(user)
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Не удалось войти')
    } finally {
      setPending(false)
    }
  }

  return (
    <div className="modal-backdrop" role="presentation" onMouseDown={onClose}>
      <section
        className="auth-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="auth-title"
        onMouseDown={(event) => event.stopPropagation()}
      >
        <button className="icon-button modal-close" type="button" onClick={onClose} aria-label="Закрыть">
          ×
        </button>
        <div className="modal-brand"><span>А</span> Affordable</div>
        <p className="eyebrow">Добро пожаловать</p>
        <h2 id="auth-title">{mode === 'login' ? 'С возвращением' : 'Создайте аккаунт'}</h2>
        <p className="muted">
          {mode === 'login'
            ? 'Войдите, чтобы добавлять организации и управлять каталогами.'
            : 'Один аккаунт — для поиска мест и публикации своего бизнеса.'}
        </p>
        <form className="auth-form" onSubmit={submit}>
          {mode === 'register' && (
            <label>Имя<input name="name" minLength={2} required placeholder="Алексей" /></label>
          )}
          <label>Email<input name="email" type="email" required placeholder="you@example.com" /></label>
          <label>Пароль<input name="password" type="password" minLength={8} required placeholder="Минимум 8 символов" /></label>
          {error && <p className="form-error" role="alert">{error}</p>}
          <button className="button button--primary button--wide" disabled={pending}>
            {pending ? 'Подождите…' : mode === 'login' ? 'Войти' : 'Зарегистрироваться'}
          </button>
        </form>
        <button className="text-button" type="button" onClick={() => { setMode(mode === 'login' ? 'register' : 'login'); setError('') }}>
          {mode === 'login' ? 'Нет аккаунта? Создать' : 'Уже есть аккаунт? Войти'}
        </button>
      </section>
    </div>
  )
}
