import { act, renderHook } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import type { CatalogItem, Organization } from '../../types'
import { usePlaceDetails } from './usePlaceDetails'

const organization = (id: string): Organization => ({
  id, type_id: 'type', owner_id: 'owner', name: id, description: null,
  address: null, city: null, latitude: null, longitude: null,
  is_active: true, created_at: '2026-01-01T00:00:00Z',
})

describe('usePlaceDetails', () => {
  it('ignores an older catalog response after another place was opened', async () => {
    let resolveFirst!: (items: CatalogItem[]) => void
    const load = (id: string) => id === 'first'
      ? new Promise<CatalogItem[]>((resolve) => { resolveFirst = resolve })
      : Promise.resolve([])
    const { result } = renderHook(() => usePlaceDetails(load))

    act(() => { void result.current.open(organization('first')) })
    await act(async () => { await result.current.open(organization('second')) })
    await act(async () => { resolveFirst([]); await Promise.resolve() })

    expect(result.current.organization?.id).toBe('second')
  })
})
