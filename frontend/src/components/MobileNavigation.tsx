import type { View } from '../ui'

export function MobileNavigation({ view, onNavigate }: { view: View; onNavigate: (view: View) => void }) {
  const destinations: Array<{ view: View; label: string; icon: string }> = [
    { view: 'discover', label: 'Подбор', icon: '⌕' },
    { view: 'places', label: 'Места', icon: '⌖' },
    { view: 'manage', label: 'Бизнес', icon: '◇' },
  ]
  return <nav className="mobile-nav" aria-label="Мобильная навигация">
    {destinations.map((item) => <button key={item.view} type="button" aria-current={view === item.view ? 'page' : undefined} onClick={() => onNavigate(item.view)}><span aria-hidden="true">{item.icon}</span>{item.label}</button>)}
  </nav>
}
