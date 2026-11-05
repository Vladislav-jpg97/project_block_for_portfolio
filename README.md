# DevTalks

## Запуск всего проекта через Docker Compose

Нужны Docker Desktop и Docker Compose. В корне репозитория выполните:

```powershell
Copy-Item .env.example .env
docker compose up --build
```

При первом запуске Compose соберёт frontend/backend, запустит PostgreSQL и
Redis, дождётся их healthcheck, применит Alembic-миграции и поднимет API.
Откройте:

- Сайт: http://localhost:3000
- API: http://localhost:8000
- Swagger: http://localhost:8000/docs

Локальные значения в `.env.example` предназначены только для разработки.
Перед публикацией измените пароли и `SECRET_KEY`.
Если порт `3000` занят, поменяйте `FRONTEND_PORT` в `.env` на `3001` и
перезапустите Compose; сайт будет доступен на `http://localhost:3001`.

Остановить контейнеры, сохранив данные:

```powershell
docker compose down
```

Посмотреть логи:

```powershell
docker compose logs -f backend frontend
```

Удалить контейнеры **и данные PostgreSQL/Redis**:

```powershell
docker compose down --volumes
```

Не выполняйте последнюю команду, если нужно сохранить локальную базу.
Подробное описание архитектуры, функций и проверок — в
[`PROJECT_DOCUMENTATION.md`](./PROJECT_DOCUMENTATION.md).