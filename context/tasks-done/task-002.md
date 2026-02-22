Сейчас при использовании ThematicBlock - `---` возникает ошибка ThematicBreak is not supported

Необходимо добавить поддердку этого функционала и добавлять разрыв страницы на его месте

## Выполнено

- В `RenderableFactory` добавлен обработчик для `extended_markdown.ThematicBreak`: возвращается `PageBreak(self._parent)`.
- Разрыв страницы реализован через существующий `renderable/page_break.py` (элемент `w:br` с `w:type="page"`).
- Тест: `tests/test_thematic_break.py` — проверка, что разбор `---` даёт один renderable типа `PageBreak`.
