import { useCallback, useEffect, useRef, useState } from 'react'
import { discoveryApi, managementApi } from '../../api/affordable'
import type { Catalog, CatalogItem, Category, Organization } from '../../types'

export interface ManagementDataApi {
  organizations: () => Promise<Organization[]>
  catalogs: (organizationId: string) => Promise<Catalog[]>
  categories: (catalogId: string) => Promise<Category[]>
  items: (catalogId: string) => Promise<CatalogItem[]>
}

const defaultApi: ManagementDataApi = {
  organizations: managementApi.myOrganizations,
  catalogs: discoveryApi.catalogs,
  categories: managementApi.categories,
  items: discoveryApi.items,
}

export function useManagementData(api: ManagementDataApi = defaultApi) {
  const [organizations, setOrganizations] = useState<Organization[]>([])
  const [selectedOrganization, setSelectedOrganization] = useState('')
  const [catalogs, setCatalogs] = useState<Catalog[]>([])
  const [selectedCatalog, setSelectedCatalog] = useState('')
  const [categories, setCategories] = useState<Category[]>([])
  const [items, setItems] = useState<CatalogItem[]>([])
  const [error, setError] = useState('')
  const organizationRequest = useRef(0)
  const catalogRequest = useRef(0)
  const detailRequest = useRef(0)

  const refreshOrganizations = useCallback(async (preferredId?: string) => {
    const request = ++organizationRequest.current
    try {
      const result = await api.organizations()
      if (request !== organizationRequest.current) return
      setOrganizations(result)
      setSelectedOrganization((current) => {
        if (preferredId && result.some((item) => item.id === preferredId)) return preferredId
        return result.some((item) => item.id === current) ? current : result[0]?.id || ''
      })
      setError('')
    } catch (reason) {
      if (request === organizationRequest.current) {
        setError(reason instanceof Error ? reason.message : 'Не удалось загрузить организации')
      }
    }
  }, [api])

  const refreshCatalogs = useCallback(async (preferredId?: string) => {
    const request = ++catalogRequest.current
    if (!selectedOrganization) {
      setCatalogs([])
      setSelectedCatalog('')
      return
    }
    try {
      const result = await api.catalogs(selectedOrganization)
      if (request !== catalogRequest.current) return
      setCatalogs(result)
      setSelectedCatalog((current) => {
        if (preferredId && result.some((item) => item.id === preferredId)) return preferredId
        return result.some((item) => item.id === current) ? current : result[0]?.id || ''
      })
      setError('')
    } catch (reason) {
      if (request === catalogRequest.current) {
        setError(reason instanceof Error ? reason.message : 'Не удалось загрузить каталоги')
      }
    }
  }, [api, selectedOrganization])

  const refreshCatalogData = useCallback(async () => {
    const request = ++detailRequest.current
    if (!selectedCatalog) {
      setCategories([])
      setItems([])
      return
    }
    try {
      const [loadedCategories, loadedItems] = await Promise.all([
        api.categories(selectedCatalog),
        api.items(selectedCatalog),
      ])
      if (request !== detailRequest.current) return
      setCategories(loadedCategories)
      setItems(loadedItems)
      setError('')
    } catch (reason) {
      if (request === detailRequest.current) {
        setError(reason instanceof Error ? reason.message : 'Не удалось загрузить каталог')
      }
    }
  }, [api, selectedCatalog])

  useEffect(() => {
    void Promise.resolve().then(() => refreshOrganizations())
    return () => { organizationRequest.current += 1 }
  }, [refreshOrganizations])

  useEffect(() => {
    void Promise.resolve().then(() => {
      setCatalogs([])
      setSelectedCatalog('')
      setCategories([])
      setItems([])
      return refreshCatalogs()
    })
    return () => { catalogRequest.current += 1 }
  }, [refreshCatalogs])

  useEffect(() => {
    void Promise.resolve().then(() => {
      setCategories([])
      setItems([])
      return refreshCatalogData()
    })
    return () => { detailRequest.current += 1 }
  }, [refreshCatalogData])

  return {
    organizations,
    selectedOrganization,
    setSelectedOrganization,
    catalogs,
    selectedCatalog,
    setSelectedCatalog,
    categories,
    items,
    error,
    clearError: () => setError(''),
    refreshOrganizations,
    refreshCatalogs,
    refreshCatalogData,
  }
}
