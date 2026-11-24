import { render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { MobileNavigation } from './MobileNavigation'

describe('MobileNavigation', () => {
  it('marks the active destination for assistive technology', () => {
    render(<MobileNavigation view="places" onNavigate={vi.fn()} />)
    expect(screen.getByRole('navigation', { name: 'Мобильная навигация' })).toBeVisible()
    expect(screen.getByRole('button', { name: 'Места' })).toHaveAttribute('aria-current', 'page')
  })
})
