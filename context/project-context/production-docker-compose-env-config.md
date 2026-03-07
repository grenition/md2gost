# Production Docker Compose env config

## Что сделано

- `docker-compose.yml` переведен на конфигурацию, пригодную для VPS/production:
  - удалены bind-mount'ы `./md2gost` и `./setup.py` из `docx-service`;
  - добавлены `restart: unless-stopped` для сервисов;
  - параметры сервисов и инфраструктуры вынесены в переменные окружения (`${...}`).
- Добавлены инфраструктурные сервисы `postgres` и `minio` в `docker-compose.yml` для production-персистентности.
- Добавлен шаблон переменных `/.env.production.example` для удобного старта.
- В `services/docx-service/app.py` загрузка сессионных изображений переведена на HTTP-доступ к `file-service` (без общего тома).
- В `services/file-service/app.py` добавлен backend `s3` (по умолчанию) и fallback `local`.
- В `services/session-service/app.py` сессии переведены в PostgreSQL (`DATABASE_URL`) без авто-истечения.
- В корневом `README.md` добавлен раздел с шагами production-деплоя и списком переменных.

## Ключевые переменные

- Сетевые: `GATEWAY_PORT`, `DOCX_SERVICE_URL`, `FILE_SERVICE_URL`, `SESSION_SERVICE_URL`
- Хранилище/сессии: `WORKING_DIR`, `TEMPLATE_PATH`, `SESSIONS_STORAGE_BASE`
- Backends: `SESSION_STORE_BACKEND`, `STORAGE_BACKEND`
- Инфраструктура: `DATABASE_URL`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `S3_ENDPOINT`, `S3_REGION`, `S3_BUCKET`, `S3_ACCESS_KEY`, `S3_SECRET_KEY`, `S3_USE_SSL`

## Проверки

- Добавлен тест `tests/test_production_compose_config.py`, который проверяет:
  - отсутствие bind-mount `./setup.py:/app/setup.py:ro` в `docker-compose.yml`;
  - наличие инфраструктурных переменных в compose;
  - наличие обязательных ключей в `.env.production.example`.
