import unittest

from md2gost.parser_ import Parser
from md2gost.renderable.heading import Heading

from . import _create_test_document


class TestHeadingNumberingSpace(unittest.TestCase):
    """Нумерованные заголовки должны иметь ведущий пробел между номером и текстом.

    Иначе при двузначной/трёхзначной нумерации (1.2.10, 1.2.100) отступ теряется
    и получается «1.2.10Описание» вместо «1.2.10 Описание».
    """

    def setUp(self) -> None:
        self._document, self._max_height, self._max_width = _create_test_document()

    def test_numbered_heading_starts_with_space(self):
        """Нумерованный заголовок (### Текст) должен начинаться с пробела в параграфе."""
        parser = Parser(self._document, "### Описание подхода к решению")
        renderables = list(parser.parse())
        self.assertEqual(len(renderables), 1, "Ожидался один элемент после разбора заголовка")
        self.assertIsInstance(
            renderables[0],
            Heading,
            f"Ожидался Heading, получен {type(renderables[0]).__name__}",
        )
        heading = renderables[0]
        self.assertTrue(
            heading.is_numbered,
            "Заголовок без * должен быть нумерованным",
        )
        para_text = heading._docx_paragraph.text
        self.assertTrue(
            para_text.startswith(" "),
            f"Текст нумерованного заголовка должен начинаться с пробела (между номером и текстом), "
            f"получено: {repr(para_text[:50])}",
        )
        self.assertIn("Описание", para_text, "Текст заголовка должен содержать содержимое")

    def test_unnumbered_heading_has_no_leading_space(self):
        """Ненумерованный заголовок (* Текст) не должен иметь ведущий пробел."""
        parser = Parser(self._document, "### * Центрированный заголовок")
        renderables = list(parser.parse())
        self.assertEqual(len(renderables), 1)
        self.assertIsInstance(renderables[0], Heading)
        heading = renderables[0]
        self.assertFalse(heading.is_numbered, "Заголовок с * не должен быть нумерованным")
        para_text = heading._docx_paragraph.text.strip()
        self.assertTrue(
            para_text.startswith("Центрированный"),
            f"Текст ненумерованного заголовка не должен начинаться с пробела: {repr(para_text[:50])}",
        )
