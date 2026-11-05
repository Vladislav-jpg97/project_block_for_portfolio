# DevTalks — документация проекта

DevTalks — русскоязычное сообщество разработчиков. Frontend использует только
реальные API Backend; функции, для которых API пока нет, не представлены как
работающие.

## Архитектура

```text
Пользователь
  |
  v
Next.js App Router (frontend/)
  |
  v
Централизованный API-клиент -> same-origin Next.js proxy
  |
  v
FastAPI (backend/src/backend)
  |
  v
Dependencies -> Services -> Repositories -> SQLAlchemy async
  |                                   |
  v                                   v
Redis cache                       PostgreSQL
```

Frontend хранит access и refresh JWT в `sessionStorage` текущей вкладки.
Просроченный access token обновляется через Backend
`POST /api/v1/auth/refresh`. Браузер отправляет API-запросы на тот же origin,
что и Next.js; серверный proxy пересылает их в Backend. В Docker Compose для
этого используется `http://backend:8000`, а при локальном запуске —
`BACKEND_API_URL` (по умолчанию `http://localhost:8000`). Пример находится в
[`frontend/.env.example`](./frontend/.env.example).

## Технологии и зависимости

**Backend:** Python 3.13+, FastAPI, Pydantic 2, SQLAlchemy async, asyncpg,
PostgreSQL, Alembic, Redis, Pillow, python-multipart, python-jose, Argon2,
Poetry.

**Frontend:** Next.js App Router, React, TypeScript, Tailwind CSS 4,
Lucide React, React Markdown, remark-gfm, ESLint.

## Запуск локально

### Docker Compose (рекомендуемый способ)

Установите Docker Desktop, в корне проекта выполните:

```powershell
Copy-Item .env.example .env
docker compose up --build
```

Compose запускает PostgreSQL, Redis, FastAPI (с автоматическим применением
миграций, включая начальные темы публикаций) и Next.js. Сайт доступен по
`http://localhost:3000`, API —
`http://localhost:8000`, Swagger — `http://localhost:8000/docs`.
Если порт `3000` уже занят, задайте `FRONTEND_PORT=3001` в корневом `.env`.
Остановить контейнеры без удаления данных: `docker compose down`. Удаление
данных вместе с контейнерами: `docker compose down --volumes`.

### Backend

Нужны PostgreSQL и Redis. В `backend/` скопируйте `.env.example` в `.env`,
задайте собственные параметры подключения и секретный ключ, затем выполните:

```powershell
Set-Location backend
poetry install
poetry run alembic upgrade head
poetry run uvicorn backend.main:app --reload
```

API: `http://localhost:8000`; документация OpenAPI: `http://localhost:8000/docs`.
Подробности: [`backend/README.md`](./backend/README.md).

### Frontend

В `frontend/` скопируйте `.env.example` в `.env.local`, проверьте
`BACKEND_API_URL`, затем выполните:

```powershell
Set-Location frontend
npm install
npm run dev
```

Сайт: `http://localhost:3000`. Другие команды: `npm run lint`,
`npm run build`.

## Реализованные сценарии

- Регистрация, вход, выход и обновление JWT.
- Лента с сортировкой и пагинацией, поиск публикаций и разработчиков.
- Публичные категории и теги.
- Создание, редактирование и удаление публикаций.
- Публикации могут быть короткими; пустой текст не принимается.
- Голоса, закладки, комментарии, ответы и удаление собственных комментариев.
- Просмотр собственных публикаций и закладок, редактирование профиля,
  загрузка/удаление аватара.
- Адаптивная навигация и светлая/тёмная тема.

В API не обнаружены подписки/друзья, уведомления, личные сообщения,
вложения-изображения в постах или восстановление пароля; интерфейс не
имитирует эти возможности. Аватары сохраняются в постоянный Docker volume.
Новая база автоматически получает стандартные темы (`Python`, `JavaScript`,
`Backend`, `Frontend`, `DevOps`, `Career`) из Alembic-миграции.

## API Endpoints

Все прикладные маршруты имеют префикс `/api/v1`.

| Метод | Endpoint | Назначение |
|---|---|---|
| GET | `/` | Проверка запуска |
| GET | `/health` | Проверка состояния |
| POST | `/auth/register` | Регистрация |
| POST | `/auth/login` | Вход и выдача токенов |
| POST | `/auth/refresh` | Обновление пары токенов |
| POST | `/auth/change-password` | Смена пароля |
| GET | `/feed/` | Пагинированная лента (`feed_type`, `page`, `size`) |
| GET / POST | `/posts/` | Поиск/список и создание публикаций |
| GET | `/posts/{slug}` | Просмотр опубликованной публикации |
| PATCH / DELETE | `/posts/{post_id}` | Изменение / удаление собственной публикации |
| PATCH | `/posts/{post_id}/publish` | Публикация черновика |
| POST / DELETE | `/posts/{post_id}/vote` | Добавить / убрать голос |
| POST / DELETE | `/posts/{post_id}/bookmark` | Добавить / убрать закладку |
| GET / POST | `/posts/{post_id}/comments/` | Список и создание комментариев/ответов |
| GET | `/posts/{post_id}/comments/{comment_id}` | Просмотр комментария |
| PUT / DELETE | `/posts/{post_id}/comments/{comment_id}` | Изменение / удаление своего комментария |
| GET | `/categories/` | Список категорий |
| GET | `/categories/{category_slug}` | Просмотр категории |
| POST | `/categories/` | Создание категории (superuser) |
| PUT / DELETE | `/categories/{category_id}` | Изменение / удаление категории (superuser) |
| GET | `/tags/` | Список тегов |
| GET | `/tags/{tag_id}` | Просмотр тега |
| POST / DELETE | `/tags/`, `/tags/{tag_id}` | Управление тегами (superuser) |
| GET | `/users/` | Поиск пользователей |
| GET / PATCH | `/users/me` | Свой профиль и его изменение |
| POST / DELETE | `/users/me/avatar` | Загрузка / удаление аватара |
| GET | `/media/avatars/{filename}` | Получение аватара |
| GET | `/users/me/bookmarks` | Сохранённые публикации |
| GET | `/users/{user_id}` | Публичный профиль |
| GET | `/users/{user_id}/posts` | Публикации пользователя |

Детали схем, доступов и ограничений см. в
[`BACKEND_AUDIT.md`](./BACKEND_AUDIT.md).

## Проверки и ограничения

**Frontend:** `npm run lint`, `npx tsc --noEmit` и `npm run build` прошли.
Производственные зависимости: `npm audit --omit=dev` — 0 уязвимостей. Полный
`npm audit` сообщает 8 moderate advisory в цепочке development-зависимостей
ESLint (`minimatch`); исправление аудитором требует force-обновления с
понижением `eslint-config-next` на несовместимую major-версию, поэтому
зависимости не менялись автоматически.

**Backend:** 18 unit-тестов прошли; `compileall`, импорт приложения и
генерация OpenAPI (25 маршрутов), `alembic heads` (один head) и генерация
offline SQL миграций прошли. Docker Compose образы собрались, все четыре
сервиса запустились; healthchecks PostgreSQL/Redis/backend прошли, миграции
применены, главная страница вернула HTTP 200 и UI загрузил API-ленту.
Через запущенный API проверены регистрация, вход, загрузка, получение и
удаление аватара; раздача изображения также проверена через Next.js proxy.
Тестовые аккаунты после проверки удалены. Полный сценарий CRUD публикаций
не проверялся; FastAPI TestClient недоступен из-за отсутствующей зависимости
`httpx2`.

До публичного production-развёртывания настройте секреты и CORS, включите
ограничение частоты запросов и предусмотрите отзыв/ротацию refresh-токенов.
