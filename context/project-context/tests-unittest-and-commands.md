# Тесты: unittest и команды

- **Директория**: `tests/`, unittest.
- **Хелпер**: `_create_test_document()` в `tests/__init__.py`.
- **Запуск** (из корня проекта): `python -m unittest discover -s tests -t . -v` (или через `./venv/bin/python` при использовании venv).
- **Тесты списков**: `tests/test_list.py` — проверка маркера (—) и нумерации (1.).
- **Примечание**: часть тестов в `test_paragraph_sizer` требует шрифты Calibri/Consolas в системе.
