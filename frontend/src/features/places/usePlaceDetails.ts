import { useCallback, useRef, useState } from 'react'
import { discoveryApi } from '../../api/affordable'
import type { CatalogItem, Organization } from '../../types'

async function loadCatalogItems(organizationId: string) {
  const catalogs = await discoveryApi.catalogs(organizationId)
  return (await Promise.all(catalogs.map((catalog) => discoveryApi.items(catalog.id)))).flat()
}

export function usePlaceDetails(load = loadCatalogItems) {
  const [organization, setOrganization] = useState<Organization | null>(null)
  const [items, setItems] = useState<CatalogItem[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const requestId = useRef(0)

  const open = useCallback(async (next: Organization, suggested: CatalogItem[] = []) => {
    const currentRequest = ++requestId.current
    setOrganization(next)
    setItems(suggested)
    setError('')
    if (suggested.length) return
    setIsLoading(true)
    try {
      const loadedItems = await load(next.id)
      if (currentRequest === requestId.current) setItems(loadedItems)
    } catch (reason) {
      if (currentRequest === requestId.current) {
        setError(reason instanceof Error ? reason.message : 'Не удалось загрузить каталог')
      }
    } finally {
      if (currentRequest === requestId.current) setIsLoading(false)
    }
  }, [load])

  const close = useCallback(() => {
    requestId.current += 1
    setOrganization(null)
    setItems([])
    setError('')
    setIsLoading(false)
  }, [])

  return { organization, items, isLoading, error, open, close }
}
