import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { AppHeader } from './AppHeader'

describe('AppHeader', () => {
  it('marks the current view and exposes login for anonymous users', async () => {
    const onLogin = vi.fn()
    render(<AppHeader view="places" user={null} onNavigate={vi.fn()} onLogin={onLogin} onLogout={vi.fn()} />)

    expect(screen.getByRole('button', { name: 'Все места' })).toHaveClass('active')
    await userEvent.click(screen.getByRole('button', { name: 'Войти' }))
    expect(onLogin).toHaveBeenCalledOnce()
  })
})
