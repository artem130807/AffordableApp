const CLIENT_ID_KEY = 'affordable.client-id'

export function getClientId(): string {
  const existing = localStorage.getItem(CLIENT_ID_KEY)
  if (existing) return existing
  const clientId = crypto.randomUUID()
  localStorage.setItem(CLIENT_ID_KEY, clientId)
  return clientId
}
