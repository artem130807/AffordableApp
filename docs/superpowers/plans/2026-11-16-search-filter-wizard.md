# Search Filter Wizard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the busy landing page with a mobile-first question wizard, persist every completed/skipped filter in PostgreSQL, and return recommendations using the captured answers.

**Architecture:** Add `RecommendationFilter` as a Clean Architecture aggregate with its own repository and CQRS handlers, then expose one transactional search endpoint that persists the filter and queries recommendations. Split frontend state into session, wizard, result and place-detail units; make the wizard a reducer-driven component with focused tests and responsive CSS.

**Tech Stack:** Python 3.12+, FastAPI, SQLAlchemy asyncio, Alembic, PostgreSQL, Pytest, React 19, TypeScript 5.9, Vite, Vitest, Testing Library.

**Spec:** `docs/superpowers/specs/2026-11-16-search-filter-wizard-design.md`

## Global Constraints

- Every CQRS use case and repository implementation remains in its own module.
- All repositories used by a request share the existing Unit of Work transaction.
- Anonymous filters use a random frontend `client_id`; no IP address is stored for analytics.
- Every question is optional; empty strings normalize to `NULL`.
- Interactive controls are at least 44×44 px and mobile content respects safe-area insets.
- Existing catalog/business-management functionality remains available after the wizard.
- New behavior follows RED → GREEN → REFACTOR.

## Review Focus

- An all-skipped anonymous wizard creates exactly one filter and returns public organizations.
- An expired access token refreshes before `/auth/me` instead of dropping a valid session.
- Double submit cannot create duplicate filters.
- Optional city/wishes values are normalized, bounded and safely applied to repository queries.
- Late place/catalog responses cannot replace the currently selected place.

---

### Task 1: RecommendationFilter persistence

**Files:**
- Create: `backend/src/app/domain/entities/recommendation_filter.py`
- Create: `backend/src/app/domain/repositories/recommendation_filter_repository.py`
- Create: `backend/src/app/infrastructure/repositories/recommendation_filter_repository.py`
- Create: `backend/src/app/application/cqrs/recommendation_filters/create_recommendation_filter.py`
- Create: `backend/src/app/application/cqrs/recommendation_filters/list_user_recommendation_filters.py`
- Create: `backend/migrations/versions/20261116_0002_recommendation_filters.py`
- Modify: entity/repository exports, ORM models, Unit of Work port/implementation
- Test: `backend/tests/test_recommendation_filters.py`

**Interfaces:**
- Produces `RecommendationFilter`, `RecommendationFilterRepository`, `CreateRecommendationFilterCommand/Handler`, and `ListUserRecommendationFiltersQuery/Handler`.
- Repository exposes `add(filter)` and `list_by_user(user_id, offset, limit)`.

- [ ] Write domain/application tests for nullable fields, validation boundaries, persistence and user history.
- [ ] Run the focused tests and confirm failure because the entity/use cases do not exist.
- [ ] Implement entity, repository, handlers, ORM model, exports and UOW registration.
- [ ] Add migration with indexes on `created_at`, `user_id`, `client_id`, `organization_type_id`, `city`.
- [ ] Run focused tests, then backend suite, Ruff and Mypy.

### Task 2: Transactional recommendation-search API

**Files:**
- Modify: `backend/src/app/application/cqrs/recommendations/find_affordable_organizations.py`
- Modify: `backend/src/app/domain/repositories/catalog_item_repository.py`
- Modify: `backend/src/app/infrastructure/repositories/catalog_item_repository.py`
- Modify: `backend/src/app/presentation/api/dependencies.py`
- Modify: `backend/src/app/presentation/api/routes/recommendations.py`
- Modify: `backend/src/app/presentation/schemas/organizations.py`
- Test: `backend/tests/test_api_flow.py`
- Test: `backend/tests/test_recommendations.py`

**Interfaces:**
- Produces `POST /api/v1/recommendation-searches` returning `{filter, recommendations}`.
- Produces `GET /api/v1/recommendation-filters/me` for authenticated history.
- Recommendation query accepts nullable budget and optional wishes.

- [ ] Add failing tests for anonymous all-skipped search, authenticated ownership/history, invalid type, optional budget and wishes matching.
- [ ] Run focused tests and verify expected 404/import/contract failures.
- [ ] Implement optional-user dependency, schemas, routes and repository filters.
- [ ] Preserve the existing GET recommendations endpoint as a compatibility wrapper.
- [ ] Run focused tests and the complete backend verification suite.

### Task 3: Frontend session and search API foundation

**Files:**
- Modify: `frontend/package.json`
- Create: `frontend/src/api/client.test.ts`
- Create: `frontend/src/api/searches.ts`
- Create: `frontend/src/session/clientId.ts`
- Create: `frontend/src/session/useSession.ts`
- Modify: `frontend/src/api/client.ts`
- Modify: `frontend/src/api/affordable.ts`
- Modify: `frontend/src/types.ts`

**Interfaces:**
- Produces `apiClient.request`, refresh-safe `/auth/me`, `getClientId()`, `searchApi.create(filter)`, and `useSession()`.

- [ ] Install Vitest, jsdom and Testing Library; add `test` script and setup.
- [ ] Add failing tests proving `/auth/me` refreshes once and concurrent 401s share one refresh.
- [ ] Implement path-specific refresh guards rather than excluding every `/auth/*` route.
- [ ] Add typed filter/search contracts and stable random `client_id` storage.
- [ ] Run frontend focused tests, ESLint and TypeScript build.

### Task 4: Reducer-driven mobile wizard

**Files:**
- Create: `frontend/src/features/search-wizard/wizardState.ts`
- Create: `frontend/src/features/search-wizard/wizardState.test.ts`
- Create: `frontend/src/features/search-wizard/SearchWizard.tsx`
- Create: `frontend/src/features/search-wizard/SearchWizard.test.tsx`
- Create: focused step components under `frontend/src/features/search-wizard/steps/`

**Interfaces:**
- Produces `SearchWizard({types, cities, onComplete})` and a pure reducer that supports answer, next, back, skip and skip-all.

- [ ] Add failing reducer tests for progression, back, single skip, skip-all and immutable draft updates.
- [ ] Implement reducer minimally and make focused tests green.
- [ ] Add failing component tests for first question, Enter progression, one-submit guard and retry preserving draft.
- [ ] Implement accessible wizard and make component tests green.
- [ ] Refactor repeated option/step chrome without changing behavior; rerun tests.

### Task 5: App decomposition and mobile presentation

**Files:**
- Create: `frontend/src/components/AppHeader.tsx`
- Create: `frontend/src/components/MobileNavigation.tsx`
- Create: `frontend/src/features/results/ResultsView.tsx`
- Create: `frontend/src/features/places/PlaceModal.tsx`
- Create: `frontend/src/features/places/usePlaceDetails.ts`
- Modify: `frontend/src/App.tsx`
- Modify: `frontend/src/components/AuthModal.tsx`
- Modify: `frontend/src/components/ManagePanel.tsx`
- Rewrite: `frontend/src/index.css`
- Test: corresponding component/hook tests

**Interfaces:**
- App composes session, wizard, results and management views without owning their internal state.
- Place detail hook aborts obsolete requests; modals close on Escape and lock background scroll.

- [ ] Add failing tests for stale place requests, Escape close and mobile navigation semantics.
- [ ] Split components/hooks and make tests green.
- [ ] Implement minimal aesthetic wizard-first design, safe-area spacing, 16 px form controls, reduced motion and focus-visible styles.
- [ ] Verify at 320, 375, 768 and desktop widths with no horizontal overflow.
- [ ] Run complete frontend tests, lint and production build.

### Task 6: Migration and whole-project verification

**Files:**
- Modify: `backend/README.md`
- Modify: root `README.md` only if startup behavior changed

**Interfaces:**
- Produces documented API/search flow and a verified deployable repository.

- [ ] Run Alembic upgrade and `alembic check` against an isolated test database.
- [ ] Run backend Pytest, Ruff, Mypy and dependency audit.
- [ ] Run frontend tests, ESLint, TypeScript/Vite build and production dependency audit.
- [ ] Perform browser QA of wizard completion, skip-all, auth restore and business cabinet on mobile and desktop.
- [ ] Review the complete diff against the design and record any deferred minor findings.
