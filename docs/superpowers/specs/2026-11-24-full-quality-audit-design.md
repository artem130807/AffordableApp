# Full quality audit design

## Intent

Довести текущий MVP Affordable до предсказуемого состояния без переписывания
работающей Clean Architecture. Исправляются доказанные дефекты поведения,
безопасности сессий, конкурентной загрузки UI и тестовой изоляции. Любое изменение
поведения закрепляется автоматическим тестом.

## Goals

- сохранить направление зависимостей `presentation -> application -> domain`;
- оставить один CQRS-handler и один repository adapter в модуле;
- устранить утечки refresh-сессий и некорректное восстановление токенов;
- сделать ответы мастера редактируемыми без скрытых старых значений;
- защитить асинхронные экраны от устаревших ответов и повторных отправок;
- покрыть отрицательные сценарии API, UnitOfWork, RBAC и frontend;
- проверить PostgreSQL-миграции, статический анализ, production build и зависимости.

## Non-goals

- новый функционал продукта и новые сущности;
- полная замена UI-kit или state manager;
- искусственное достижение 100% line coverage;
- массовый DDD-рефакторинг стабильных модулей.

## Approaches considered

1. **Только увеличить число тестов.** Быстро, но тесты зафиксируют уже неверное
   поведение logout и мастера.
2. **Риск-ориентированный аудит и точечный рефакторинг — выбран.** Тест сначала,
   затем минимальное исправление и локальное разделение ответственности.
3. **Полная переработка по vertical slices.** Теоретически чище, но создаёт слишком
   большой diff и риск регрессий для MVP без продуктовой пользы.

## Backend decisions

- `POST /auth/logout` аутентифицируется самим refresh-токеном и не требует живого
  access-токена. Это исключает ротацию access/refresh прямо перед logout и
  оставшийся активным новый refresh-токен.
- malformed password hash всегда даёт отказ входа, а не HTTP 500.
- транзакционный тест поиска доказывает, что сохранённый фильтр откатывается, если
  подбор рекомендаций завершился ошибкой.
- тесты API получают явную изоляцию состояния; PostgreSQL DDL проверяется Alembic.
- существующие UOW/repository/CQRS границы сохраняются; архитектурные тесты
  усиливаются только инвариантами, которые реально нужны проекту.

## Frontend decisions

- токены из localStorage и refresh-response проходят runtime-проверку формы;
  повреждённые данные удаляются.
- logout не запускает автоматический refresh и очищает React-сессию даже при
  сетевой ошибке.
- шаг мастера владеет значением в reducer: возврат показывает сохранённый ответ,
  а «Пропустить» удаляет ответ текущего шага.
- загрузка организаций/каталогов/позиций защищается sequence id или отменой, чтобы
  более старый response не перезаписывал новое состояние.
- AuthModal получает Escape, блокировку прокрутки и корректное восстановление.

## Testing strategy

- backend unit tests: security, handlers, recommendation calculation, UOW;
- backend API tests: auth lifecycle, validation, ownership/RBAC, atomic search;
- frontend unit/component tests: API client, session, wizard, modal, management races;
- architecture tests: отсутствие infrastructure/presentation imports во внутренних
  слоях, один handler/repository на модуль;
- final gates: pytest, Ruff, strict MyPy, Alembic offline SQL, Vitest, ESLint,
  TypeScript/Vite build, dependency audits.

## Constraints

Проект остаётся FastAPI + async SQLAlchemy + PostgreSQL и React 19 + TypeScript.
Существующие неотслеживаемые файлы принадлежат пользователю: не выполнять
автоматический массовый commit, reset или cleanup.
