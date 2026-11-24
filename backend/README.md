# Backend

FastAPI-приложение с зависимостями, направленными к центру:

```text
presentation -> application -> domain
infrastructure -> application/domain
```

## Команды

```powershell
docker compose up -d postgres
Copy-Item .env.example .env
python -m pip install -e ".[dev]"
alembic upgrade head
uvicorn app.main:app --reload
pytest --cov=app --cov-branch --cov-report=term-missing
ruff check .
mypy
pip-audit --cache-dir .pip-audit-cache
```

## Структура

- `domain` — бизнес-сущности и правила без зависимостей от фреймворка.
- `application` — сценарии использования и интерфейсы (порты).
- `infrastructure` — конфигурация и внешние реализации.
- `presentation` — HTTP-контроллеры, схемы и маршруты FastAPI.

## Предметная область

Универсальная структура `OrganizationType → Organization → Catalog →
ItemCategory/CatalogItem` позволяет хранить рестораны, театры, магазины и другие
места в одной модели. Позиция каталога содержит цену, валюту, единицу цены и
произвольные JSON-атрибуты (например, `serves`, длительность или характеристики).

Для каждой хранимой сущности в `application/cqrs` есть отдельная папка, а каждый
use case размещён в собственном модуле: например, `users/create_user.py`,
`auth/login_user.py`, `refresh_tokens/rotate_refresh_token.py`. Один модуль
содержит не более одного handler-класса.

Repository ports и SQLAlchemy Async adapters также разделены по сущностям в
`domain/repositories` и `infrastructure/repositories`. Их `__init__.py` содержат
только реэкспорты и не объединяют бизнес-логику.

Транзакционная граница оформлена через application-порт `UnitOfWork` и
`SqlAlchemyUnitOfWork`. На один HTTP-запрос создаётся одна сессия и один набор
репозиториев: успешный запрос фиксируется целиком, ошибка откатывает все сделанные
изменения. Роуты получают репозитории только из Unit of Work и не создают
SQLAlchemy-адаптеры вручную.

Основная база данных — PostgreSQL, подключение выполняется асинхронно через
`asyncpg`. Локальный контейнер описан в `compose.yaml`, строка подключения — в
`.env.example`. SQLite используется только внутри автоматических тестов как
быстрый изолированный адаптер репозиториев.

Схема PostgreSQL управляется Alembic. Приложение не выполняет `create_all` в
обычном режиме: перед запуском применяется `alembic upgrade head`. Флаг
`APP_AUTO_CREATE_SCHEMA=true` предназначен только для изолированных тестов.

## Аутентификация и права

- access JWT живёт 15 минут по умолчанию;
- JWT проверяет обязательные claims, issuer и audience; `APP_JWT_SECRET` обязателен;
- refresh-токены ротируются, хранятся только как SHA-256 хеши и могут быть отозваны;
- logout принимает refresh-токен без обязательного access JWT, поэтому завершение
  сессии остаётся надёжным даже после истечения access-токена;
- ротация блокирует строку токена, а обнаружение повторного использования отзывает
  все активные сессии пользователя;
- permissions хранятся в отдельной таблице и связаны с ролями через
  many-to-many таблицу `role_permissions`;
- роли агрегируют права, а эндпоинты защищены permission-политиками по
  стабильному полю `Permission.code`;
- пользователь может управлять только каталогами принадлежащих ему организаций;
- начального администратора можно безопасно создать через переменные
  `APP_BOOTSTRAP_ADMIN_EMAIL` и `APP_BOOTSTRAP_ADMIN_PASSWORD`.

Основные маршруты доступны в Swagger UI по адресу <http://localhost:8000/docs>.
Поиск вариантов под бюджет: `GET /api/v1/recommendations`.
Новый сценарий подбора использует `POST /api/v1/recommendation-searches`: он в
одной транзакции сохраняет ответы пользователя в `recommendation_filters` и
возвращает найденные предложения. Все вопросы можно пропускать; анонимные
запросы связываются стабильным `client_id`, авторизованные — также с `user_id`.
История текущего пользователя доступна через
`GET /api/v1/recommendation-filters/me`.
Проверки состояния: `GET /api/v1/health` (liveness) и
`GET /api/v1/health/ready` (готовность PostgreSQL).

Управление правами администратора:

- `GET/POST /api/v1/permissions`;
- `GET/POST /api/v1/roles`;
- `POST /api/v1/roles/{role_id}/permissions`.
