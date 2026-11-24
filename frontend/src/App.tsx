import { useEffect, useMemo, useState } from 'react'
import { discoveryApi } from './api/affordable'
import { searchApi } from './api/searches'
import { AppHeader } from './components/AppHeader'
import { AuthModal } from './components/AuthModal'
import { ManagePanel } from './components/ManagePanel'
import { MobileNavigation } from './components/MobileNavigation'
import { PlaceModal } from './components/PlaceModal'
import { PlacesView } from './features/places/PlacesView'
import { usePlaceDetails } from './features/places/usePlaceDetails'
import { ResultsView } from './features/results/ResultsView'
import { SearchWizard } from './features/search-wizard/SearchWizard'
import { useSession } from './session/useSession'
import type { Organization, OrganizationType, RecommendationSearch } from './types'
import type { View } from './ui'

function App() {
  const [view, setView] = useState<View>('discover')
  const [types, setTypes] = useState<OrganizationType[]>([])
  const [organizations, setOrganizations] = useState<Organization[]>([])
  const [search, setSearch] = useState<RecommendationSearch | null>(null)
  const [authOpen, setAuthOpen] = useState(false)
  const [isLoadingDiscovery, setIsLoadingDiscovery] = useState(true)
  const [discoveryError, setDiscoveryError] = useState('')
  const { user, setUser, logout } = useSession()
  const place = usePlaceDetails()

  useEffect(() => {
    void Promise.all([discoveryApi.organizationTypes(), discoveryApi.organizations()])
      .then(([loadedTypes, loadedOrganizations]) => {
        setTypes(loadedTypes)
        setOrganizations(loadedOrganizations)
      })
      .catch((reason: Error) => setDiscoveryError(reason.message))
      .finally(() => setIsLoadingDiscovery(false))
  }, [])

  const cities = useMemo(() => [...new Set(organizations.map((item) => item.city).filter((city): city is string => Boolean(city)))].sort(), [organizations])

  async function completeSearch(draft: Parameters<typeof searchApi.create>[0]) {
    setSearch(await searchApi.create(draft))
  }

  function navigate(next: View) {
    if (next === 'manage' && !user) { setAuthOpen(true); return }
    if (next === 'discover') setSearch(null)
    setView(next)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  async function handleLogout() {
    await logout()
    navigate('discover')
  }

  const wizardIsOpen = view === 'discover' && !search

  return <div className="app-shell">
    {!wizardIsOpen && <AppHeader view={view} user={user} onNavigate={navigate} onLogin={() => setAuthOpen(true)} onLogout={() => void handleLogout()} />}

    {view === 'discover' && (search
      ? <ResultsView filter={search.filter} recommendations={search.recommendations} types={types} onOpen={(organization, items) => void place.open(organization, items)} onRestart={() => setSearch(null)} />
      : <SearchWizard types={types} cities={cities} isLoadingTypes={isLoadingDiscovery} discoveryError={discoveryError} onComplete={completeSearch} />)}
    {view === 'places' && <PlacesView organizations={organizations} types={types} error={discoveryError} onOpen={(organization) => void place.open(organization)} />}
    {view === 'manage' && user && <ManagePanel user={user} types={types} />}

    {!wizardIsOpen && <MobileNavigation view={view} onNavigate={navigate} />}
    {authOpen && <AuthModal onClose={() => setAuthOpen(false)} onAuthenticated={(authenticatedUser) => { setUser(authenticatedUser); setAuthOpen(false); setView('manage') }} />}
    {place.organization && <PlaceModal organization={place.organization} type={types.find((type) => type.id === place.organization?.type_id)} items={place.items} isLoading={place.isLoading} error={place.error} onClose={place.close} />}
  </div>
}

export default App
