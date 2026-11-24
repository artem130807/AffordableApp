# Frontend

Мобильный React + TypeScript интерфейс для пошагового подбора мест по типу,
бюджету, размеру компании, городу и пожеланиям.

## Команды

```powershell
npm install
npm run dev
npm run test:coverage
npm run lint
npm run build
```

Адрес API задаётся переменной `VITE_API_URL`; пример находится в `.env.example`.
Сессия хранит пару access/refresh токенов, автоматически обновляет истёкший
access-токен один раз и очищается при некорректном ответе авторизации.
