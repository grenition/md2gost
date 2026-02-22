"""Renderable that outputs a list of renderables (paragraphs and images) in source order."""
from copy import copy
from typing import Generator

from docx.shared import Parented

from . import Renderable
from ..layout_tracker import LayoutState
from ..rendered_info import RenderedInfo
from ..sub_renderable import SubRenderable


class ContentSequence(Renderable):
    """Holds a list of renderables (e.g. Paragraph, Image) and yields their output in order.
    Used for markdown paragraphs with inline images so that each image appears between
    the correct text segments."""
    def __init__(self, parent: Parented, items: list[Renderable]):
        self._parent = parent
        self._items = items

    def render(self, previous_rendered: RenderedInfo, layout_state: LayoutState)\
            -> Generator[RenderedInfo | SubRenderable, None, None]:
        for item in self._items:
            for info in item.render(previous_rendered, copy(layout_state)):
                if isinstance(info, RenderedInfo):
                    previous_rendered = info
                    layout_state.add_height(info.height)
                yield info
