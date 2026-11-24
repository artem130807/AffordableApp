import { fireEvent, render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { AuthModal } from './AuthModal'

describe('AuthModal', () => {
  it('closes with Escape and restores body scrolling after unmount', () => {
    const onClose = vi.fn()
    const { unmount } = render(<AuthModal onClose={onClose} onAuthenticated={vi.fn()} />)

    expect(screen.getByRole('dialog', { name: 'С возвращением' })).toBeVisible()
    expect(document.body.style.overflow).toBe('hidden')
    fireEvent.keyDown(document, { key: 'Escape' })
    expect(onClose).toHaveBeenCalledOnce()
    unmount()
    expect(document.body.style.overflow).toBe('')
  })
})
