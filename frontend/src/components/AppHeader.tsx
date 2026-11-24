import type { User } from '../types'
import type { View } from '../ui'

export function AppHeader({ view, user, onNavigate, onLogin, onLogout }: {
  view: View
  user: User | null
  onNavigate: (view: View) => void
  onLogin: () => void
  onLogout: () => void
}) {
  return <header className="site-header">
    <button className="brand" type="button" onClick={() => onNavigate('discover')} aria-label="Affordable — новый подбор"><span className="brand-mark">А</span><span>Affordable</span></button>
    <nav aria-label="Основная навигация">
      <button className={view === 'discover' ? 'active' : ''} onClick={() => onNavigate('discover')}>Подбор</button>
      <button className={view === 'places' ? 'active' : ''} onClick={() => onNavigate('places')}>Все места</button>
      <button className={view === 'manage' ? 'active' : ''} onClick={() => onNavigate('manage')}>Для бизнеса</button>
    </nav>
    <div className="header-actions">{user ? <><button className="profile-button" onClick={() => onNavigate('manage')}><span>{user.name.slice(0, 1).toUpperCase()}</span><b>{user.name}</b></button><button className="icon-button logout-button" onClick={onLogout} aria-label="Выйти">↗</button></> : <button className="button button--dark" onClick={onLogin}>Войти</button>}</div>
  </header>
}
