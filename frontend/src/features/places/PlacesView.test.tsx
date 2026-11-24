import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { PlacesView } from './PlacesView'

describe('PlacesView', () => {
  it('renders an organization and reports the selected place', async () => {
    const organization = { id: 'org', type_id: 'type', owner_id: 'owner', name: 'Театр', description: null, address: null, city: null, latitude: null, longitude: null, is_active: true, created_at: '2026-01-01T00:00:00Z' }
    const onOpen = vi.fn()
    render(<PlacesView organizations={[organization]} types={[]} onOpen={onOpen} />)

    await userEvent.click(screen.getByRole('button', { name: /Театр/ }))
    expect(onOpen).toHaveBeenCalledWith(organization)
    expect(screen.getByText('1 мест')).toBeVisible()
  })
})
