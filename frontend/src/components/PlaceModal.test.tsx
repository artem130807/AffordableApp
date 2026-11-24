import { fireEvent, render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { PlaceModal } from './PlaceModal'

describe('PlaceModal', () => {
  it('closes with Escape and restores page scrolling', () => {
    const onClose = vi.fn()
    const { unmount } = render(<PlaceModal organization={{
      id: '1', type_id: 'type', owner_id: 'owner', name: 'Театр',
      description: null, address: null, city: 'Астрахань', latitude: null,
      longitude: null, is_active: true, created_at: '2026-01-01T00:00:00Z',
    }} items={[]} onClose={onClose} />)

    expect(screen.getByRole('dialog', { name: 'Театр' })).toBeVisible()
    expect(document.body.style.overflow).toBe('hidden')
    fireEvent.keyDown(document, { key: 'Escape' })
    expect(onClose).toHaveBeenCalledOnce()
    unmount()
    expect(document.body.style.overflow).toBe('')
  })
})
