import { describe, expect, it } from 'vitest'
import { getClientId } from './clientId'

describe('getClientId', () => {
  it('creates one stable UUID for anonymous analytics', () => {
    const first = getClientId()
    const second = getClientId()

    expect(second).toBe(first)
    expect(first).toMatch(
      /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i,
    )
  })
})
