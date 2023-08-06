from looqbox.render.abstract_render import BaseRender
from looqbox.objects.looq_object import LooqObject


class ObjPDF(LooqObject):
    """
    Renders a PDF in the Looqbox's board using a PDF from the same directory of
    the response or from an external link (only works with HTTPS links).

    Attributes:
    --------
        :param str src: PDF's source.
        :param int initial_page: Page that the PDF will open.
        :param float (oercent) default_scale: Page's default scale
        :param str tab_label: Set the name of the tab in the frame.
        :param CssOption: set the correspond css property.

    Example:
    --------
    >>> from looqbox import CssOption as css
    >>> pdf = ObjPDF(src="cartaoCNPJLooqbox.pdf", default_scale=0.85,css_options=[css.Height(200), css.Width(400)])

    Properties:
    --------
        to_json_structure()
            :return: A JSON string.
    """
    def __init__(self, src, initial_page=1, default_scale=1.0, tab_label=None, value=None, **properties):

        super().__init__(**properties)
        self.source = src
        self.initial_page = initial_page
        self.tab_label = tab_label
        self.value = value
        self.default_scale = default_scale

    def to_json_structure(self, visitor: BaseRender):
        return visitor.pdf_render(self)
