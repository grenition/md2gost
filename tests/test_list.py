import unittest

from md2gost.layout_tracker import LayoutTracker
from md2gost.renderable.list import List

from . import _create_test_document


class TestList(unittest.TestCase):
    def setUp(self) -> None:
        self._document, self._max_height, self._max_width = _create_test_document()

    def test_unordered_list_uses_em_dash_bullet(self):
        """Неупорядоченный список должен использовать длинное тире (—) как маркер, не точку (●)."""
        body = self._document._body
        layout_tracker = LayoutTracker(self._max_height, self._max_width)

        lst = List(body, ordered=False)
        item_para = lst.add_item(1)
        item_para.add_run("first item")
        list(lst.render(None, layout_tracker.current_state))

        # Текст пункта списка: маркер + таб + содержимое
        list_item_paragraph = lst._paragraphs[0]._docx_paragraph
        self.assertTrue(
            list_item_paragraph.text.startswith("—"),
            f"Ожидалось начало параграфа с длинного тире (—), получено: {repr(list_item_paragraph.text[:50])}",
        )

    def test_ordered_list_unchanged(self):
        """Упорядоченный список по-прежнему использует нумерацию вида '1.'."""
        body = self._document._body
        layout_tracker = LayoutTracker(self._max_height, self._max_width)

        lst = List(body, ordered=True)
        item_para = lst.add_item(1)
        item_para.add_run("first")
        list(lst.render(None, layout_tracker.current_state))

        list_item_paragraph = lst._paragraphs[0]._docx_paragraph
        self.assertTrue(
            list_item_paragraph.text.startswith("1."),
            f"Ожидалось начало параграфа с '1.', получено: {repr(list_item_paragraph.text[:50])}",
        )
