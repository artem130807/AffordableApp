import { act, renderHook, waitFor } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const tokens = {
  access_token: 'access-token',
  refresh_token: 'refresh-token',
  token_type: 'bearer',
}

describe('useSession', () => {
  beforeEach(() => {
    vi.resetModules()
    localStorage.setItem('affordable.auth', JSON.stringify(tokens))
  })

  it('clears the in-memory user even when the logout request fails', async () => {
    const user = { id: 'user-1', email: 'user@example.com', name: 'User', is_active: true, roles: [] }
    const fetchMock = vi.fn<typeof fetch>((input) => {
      if (String(input).endsWith('/auth/me')) {
        return Promise.resolve(new Response(JSON.stringify(user), { status: 200 }))
      }
      return Promise.reject(new Error('network unavailable'))
    })
    vi.stubGlobal('fetch', fetchMock)
    const { useSession } = await import('./useSession')
    const { result } = renderHook(() => useSession())
    await waitFor(() => expect(result.current.user?.id).toBe('user-1'))

    await act(async () => {
      await expect(result.current.logout()).rejects.toThrow('network unavailable')
    })

    expect(result.current.user).toBeNull()
    expect(localStorage.getItem('affordable.auth')).toBeNull()
  })
})
