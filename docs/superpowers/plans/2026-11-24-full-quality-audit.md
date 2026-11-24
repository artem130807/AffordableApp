# Full Quality Audit Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Исправить доказанные дефекты backend/frontend и закрепить критические сценарии полноценным набором тестов.

**Architecture:** Сохранить Clean Architecture и существующие CQRS/UOW границы. Выполнять небольшие исправления по рискам, выносить только состояние с отдельной ответственностью и начинать каждый пункт с RED-теста.

**Tech Stack:** Python 3.12, FastAPI, SQLAlchemy asyncio, PostgreSQL/Alembic, Pytest, React 19, TypeScript, Vitest, Testing Library, Vite.

**Spec:** `docs/superpowers/specs/2026-11-24-full-quality-audit-design.md`

## Global Constraints

- Не менять предметную модель и публичный API без исправления доказанного дефекта.
- Один CQRS handler и один repository adapter на файл.
- PostgreSQL остаётся production DB; SQLite допустим только как быстрый test adapter.
- Не коммитить автоматически существующий неотслеживаемый проект.

## Review Focus

- Истёкший access-токен во время logout не должен оставлять активный refresh-токен.
- Повреждённая localStorage-сессия не должна считаться действующей.
- Возврат назад и skip не должны отправлять скрытое старое значение фильтра.
- Медленный старый response не должен перезаписывать выбранную организацию/каталог.
- Ошибка после сохранения RecommendationFilter должна откатывать всю транзакцию.

---

### Task 1: Authentication lifecycle hardening

**Files:**
- Modify: `backend/src/app/presentation/api/routes/auth.py`
- Modify: `backend/src/app/infrastructure/security.py`
- Test: `backend/tests/test_security.py`
- Test: `backend/tests/test_api_flow.py`

**Interfaces:**
- Produces: public idempotent `POST /api/v1/auth/logout` accepting `RefreshRequest`.

- [x] Add RED tests for logout without access token, double logout and malformed stored password hash.
- [x] Make logout revoke by refresh token without `CurrentUser` dependency.
- [x] Broaden safe malformed-hash handling without accepting invalid hashes.
- [x] Run focused tests, Ruff and MyPy.

### Task 2: Atomic search and recommendation edge cases

**Files:**
- Modify: `backend/tests/test_recommendation_searches.py`
- Modify: `backend/tests/test_recommendation_filters.py`
- Modify only if tests expose a defect: recommendation CQRS/repositories/dependency UOW.

**Interfaces:**
- Consumes: `provide_unit_of_work()` commit/rollback boundary.
- Produces: proven rollback and deterministic budget behavior.

- [x] Add RED/characterization tests for zero budget, per-person/ticket totals, limit ordering, wishes/city normalization and query failure rollback.
- [x] Implement only behavior required by failing cases.
- [x] Run all backend tests and static analysis.

### Task 3: Frontend token and session correctness

**Files:**
- Modify: `frontend/src/api/client.ts`
- Modify: `frontend/src/api/affordable.ts`
- Modify: `frontend/src/session/useSession.ts`
- Test: `frontend/src/api/client.test.ts`
- Create: `frontend/src/session/useSession.test.tsx`

**Interfaces:**
- Produces: validated token storage and logout that always clears local UI state.

- [x] Add RED tests for malformed storage, malformed refresh response, logout without refresh retry and failed logout cleanup.
- [x] Implement token type guard and public logout path.
- [x] Move session cleanup into `finally`.
- [x] Run focused tests, ESLint and TypeScript build.

### Task 4: Editable search wizard

**Files:**
- Modify: `frontend/src/features/search-wizard/wizardState.ts`
- Modify: `frontend/src/features/search-wizard/SearchWizard.tsx`
- Modify: `frontend/src/features/search-wizard/steps/NumberStep.tsx`
- Modify: `frontend/src/features/search-wizard/steps/OptionStep.tsx`
- Modify: `frontend/src/features/search-wizard/steps/TextStep.tsx`
- Test: wizard reducer/component tests.

**Interfaces:**
- Produces: controlled step values and skip semantics that delete the current field.

- [x] Add RED reducer test proving skip removes a previous answer.
- [x] Add RED component test proving back restores and edits budget/city.
- [x] Pass initial/selected values from reducer and remove unused completion state.
- [x] Run wizard tests and frontend gates.

### Task 5: Async management and modal resilience

**Files:**
- Refactor: `frontend/src/components/ManagePanel.tsx`
- Create: `frontend/src/features/management/useManagementData.ts`
- Create: `frontend/src/features/management/useManagementData.test.tsx`
- Modify: `frontend/src/components/AuthModal.tsx`
- Create: `frontend/src/components/AuthModal.test.tsx`

**Interfaces:**
- Produces: stale-response-safe management hook and accessible auth modal.

- [x] Add RED race test for organization/catalog switching.
- [x] Extract data loading and sequence protection from presentation component.
- [x] Add RED Escape/body-scroll tests for AuthModal and implement cleanup.
- [x] Add pending guards and clear stale notices around mutations.
- [x] Run all frontend tests and static gates.

### Task 6: Test isolation, architecture audit and final verification

**Files:**
- Modify: `backend/tests/conftest.py`
- Modify: `backend/tests/test_architecture.py`
- Modify: project READMEs only for changed behavior.

**Interfaces:**
- Produces: repeatable suite and documented verification evidence.

- [x] Prove API tests pass independently and in repeated full-suite execution (random-order plugin is not installed).
- [x] Add architecture assertions for route/UOW boundaries and focused module size responsibilities where objective.
- [x] Generate Alembic PostgreSQL SQL to `head` and inspect constraints/indexes.
- [x] Run pytest, Ruff, strict MyPy, Vitest, ESLint, Vite build and dependency audits.
- [x] Review the final diff for secrets, dead code, TODOs and unrelated changes.
