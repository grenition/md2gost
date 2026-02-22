# Thematic break (`---`) → разрыв страницы

- **Markdown**: горизонтальное правило `---` парсится marko как блок `ThematicBreak` (из `marko.block`).
- **Фабрика**: в `md2gost/renderable_factory.py` зарегистрирован обработчик `ThematicBreak` → возвращается `PageBreak(self._parent)`.
- **PageBreak**: `md2gost/renderable/page_break.py` — создаёт параграф с `w:br` атрибут `w:type="page"`, при рендере в документ вставляется разрыв страницы.
- **Тесты**: `tests/test_thematic_break.py` — проверка, что `Parser(document, "---")` выдаёт один renderable типа `PageBreak`.
