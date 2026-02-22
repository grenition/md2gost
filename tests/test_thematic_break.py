import unittest

from md2gost.parser_ import Parser
from md2gost.renderable.page_break import PageBreak

from . import _create_test_document


class TestThematicBreak(unittest.TestCase):
    """Thematic break (`---`) должен превращаться в разрыв страницы (PageBreak)."""

    def setUp(self) -> None:
        self._document, self._max_height, self._max_width = _create_test_document()

    def test_thematic_break_yields_page_break(self):
        """Разбор `---` должен давать один renderable типа PageBreak (разрыв страницы)."""
        parser = Parser(self._document, "---")
        renderables = list(parser.parse())
        self.assertEqual(len(renderables), 1, "Ожидался один элемент после разбора '---'")
        self.assertIsInstance(
            renderables[0],
            PageBreak,
            f"Ожидался PageBreak, получен {type(renderables[0]).__name__}",
        )
