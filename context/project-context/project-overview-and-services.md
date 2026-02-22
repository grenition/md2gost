# Обзор проекта и сервисы

- **Назначение**: конвертер Markdown → DOCX в формате ГОСТ (микросервисное веб-приложение).
- **Ядро**: библиотека `md2gost/` (Python) — рендер Markdown в docx через python-docx.
- **Сервисы**: gateway (Nginx), frontend (React), api-service (ASP.NET Core), docx-service (Flask), file-service, session-service.
