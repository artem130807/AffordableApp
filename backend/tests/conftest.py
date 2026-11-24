import os

# The application uses PostgreSQL. Tests run through the same SQLAlchemy repositories
# with an isolated in-memory adapter, so the suite does not require external services.
os.environ["APP_DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["APP_ENV"] = "test"
os.environ["APP_AUTO_CREATE_SCHEMA"] = "true"
os.environ["APP_JWT_SECRET"] = "a-secure-test-secret-with-32-characters"
os.environ["APP_BOOTSTRAP_ADMIN_EMAIL"] = "admin@example.com"
os.environ["APP_BOOTSTRAP_ADMIN_PASSWORD"] = "test-admin-password"
