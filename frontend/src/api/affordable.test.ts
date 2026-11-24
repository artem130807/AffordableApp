import { beforeEach, describe, expect, it, vi } from 'vitest'

describe('authApi', () => {
  beforeEach(() => {
    vi.resetModules()
  })

  it('allows register to be passed as a standalone callback', async () => {
    const tokens = { access_token: 'access', refresh_token: 'refresh', token_type: 'bearer' }
    const user = { id: 'user', email: 'u@example.com', name: 'User', is_active: true, roles: [] }
    const fetchMock = vi
      .fn<typeof fetch>()
      .mockResolvedValueOnce(new Response(JSON.stringify(user), { status: 201 }))
      .mockResolvedValueOnce(new Response(JSON.stringify(tokens), { status: 200 }))
      .mockResolvedValueOnce(new Response(JSON.stringify(user), { status: 200 }))
    vi.stubGlobal('fetch', fetchMock)
    const { authApi } = await import('./affordable')
    const register = authApi.register

    await expect(register('User', 'u@example.com', 'strong-password')).resolves.toEqual(user)
  })
})
